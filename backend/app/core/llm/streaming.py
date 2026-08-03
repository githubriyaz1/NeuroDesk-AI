import asyncio
import json
import time
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Dict, List, Optional
from uuid import UUID, uuid4

from app.core.logging import logger
from app.models.chat import MessageStatus
from app.schemas.chat import StreamingChunk


class CancellationManager:
    """Thread-safe stream cancellation registry."""

    def __init__(self):
        self._cancelled_streams: set[str] = set()

    def request_cancellation(self, stream_id: str) -> None:
        self._cancelled_streams.add(stream_id)
        logger.info(f"Requested cancellation for stream [{stream_id}]")

    def is_cancelled(self, stream_id: str) -> bool:
        return stream_id in self._cancelled_streams

    def clear(self, stream_id: str) -> None:
        self._cancelled_streams.discard(stream_id)


cancellation_manager = CancellationManager()


class StreamCache:
    """In-memory chunk cache per stream_id for reconnect recovery and chunk replay."""

    def __init__(self, max_chunks_per_stream: int = 200):
        self._cache: Dict[str, List[StreamingChunk]] = {}
        self.max_chunks_per_stream = max_chunks_per_stream

    def add_chunk(self, chunk: StreamingChunk) -> None:
        stream_id = chunk.stream_id
        if stream_id not in self._cache:
            self._cache[stream_id] = []
        
        self._cache[stream_id].append(chunk)
        if len(self._cache[stream_id]) > self.max_chunks_per_stream:
            self._cache[stream_id].pop(0)

    def get_chunks_since(self, stream_id: str, last_chunk_index: int = -1) -> List[StreamingChunk]:
        chunks = self._cache.get(stream_id, [])
        return [c for c in chunks if c.chunk_index > last_chunk_index]

    def clear_stream(self, stream_id: str) -> None:
        self._cache.pop(stream_id, None)


stream_cache = StreamCache()


class ResponseAssembler:
    """Assembles streamed chunks into full text and calculates metrics."""

    def __init__(self, stream_id: str, conversation_id: UUID, message_id: UUID):
        self.stream_id = stream_id
        self.conversation_id = conversation_id
        self.message_id = message_id
        self.chunks: List[str] = []
        self.start_time = time.time()
        self.completion_status = MessageStatus.STREAMING.value

    def append_chunk(self, content: str) -> None:
        self.chunks.append(content)

    def get_assembled_content(self) -> str:
        return "".join(self.chunks)

    def finalize(self, status: str = MessageStatus.COMPLETED.value) -> Dict[str, Any]:
        self.completion_status = status
        latency_ms = round((time.time() - self.start_time) * 1000, 2)
        full_content = self.get_assembled_content()
        token_count = math.ceil(len(full_content) / 4) if full_content else 0

        return {
            "content": full_content,
            "markdown": full_content,
            "status": status,
            "latency_ms": latency_ms,
            "token_usage": {
                "prompt_tokens": 0,
                "completion_tokens": token_count,
                "total_tokens": token_count,
            },
        }


class StreamingSessionManager:
    """Orchestrates SSE frame generation, sequence ordering, heartbeats, and cancellation."""

    def __init__(self):
        self.cancellation = cancellation_manager
        self.cache = stream_cache

    async def stream_generator(
        self,
        conversation_id: UUID,
        message_id: UUID,
        chunk_stream: AsyncGenerator[str, None],
        stream_id: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        stream_id = stream_id or str(uuid4())
        chunk_index = 0
        assembler = ResponseAssembler(stream_id, conversation_id, message_id)

        try:
            async for text_delta in chunk_stream:
                if self.cancellation.is_cancelled(stream_id):
                    logger.info(f"Stream [{stream_id}] cancelled during generation.")
                    assembler.finalize(MessageStatus.CANCELLED.value)
                    
                    cancel_chunk = StreamingChunk(
                        stream_id=stream_id,
                        conversation_id=conversation_id,
                        message_id=message_id,
                        chunk_index=chunk_index,
                        content="\n[Generation Cancelled]",
                        is_final=True,
                        timestamp=datetime.now(timezone.utc),
                    )
                    self.cache.add_chunk(cancel_chunk)
                    yield f"data: {cancel_chunk.model_dump_json()}\n\n"
                    break

                assembler.append_chunk(text_delta)
                chunk = StreamingChunk(
                    stream_id=stream_id,
                    conversation_id=conversation_id,
                    message_id=message_id,
                    chunk_index=chunk_index,
                    content=text_delta,
                    is_final=False,
                    timestamp=datetime.now(timezone.utc),
                )
                self.cache.add_chunk(chunk)
                yield f"data: {chunk.model_dump_json()}\n\n"
                chunk_index += 1
                await asyncio.sleep(0.01)  # Non-blocking yield

            if not self.cancellation.is_cancelled(stream_id):
                final_chunk = StreamingChunk(
                    stream_id=stream_id,
                    conversation_id=conversation_id,
                    message_id=message_id,
                    chunk_index=chunk_index,
                    content="",
                    is_final=True,
                    timestamp=datetime.now(timezone.utc),
                )
                self.cache.add_chunk(final_chunk)
                yield f"data: {final_chunk.model_dump_json()}\n\n"

        except Exception as exc:
            logger.error(f"Error during SSE stream [{stream_id}]: {exc}")
            err_chunk = StreamingChunk(
                stream_id=stream_id,
                conversation_id=conversation_id,
                message_id=message_id,
                chunk_index=chunk_index,
                content=f"\n[Stream Error: {str(exc)}]",
                is_final=True,
                timestamp=datetime.now(timezone.utc),
            )
            yield f"data: {err_chunk.model_dump_json()}\n\n"
        finally:
            self.cancellation.clear(stream_id)


streaming_session_manager = StreamingSessionManager()
