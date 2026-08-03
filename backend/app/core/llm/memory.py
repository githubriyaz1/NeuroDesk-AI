import json
import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from app.core.config import settings
from app.core.logging import logger
from app.models.chat import Conversation, ChatMessage, MessageRole


class TokenBudgetManager:
    """Calculates and manages context window token budgets."""

    def __init__(self, max_context_tokens: int = 32000, reserved_output_tokens: int = 4096):
        self.max_context_tokens = max_context_tokens
        self.reserved_output_tokens = reserved_output_tokens

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Heuristic estimation of token count (~4 characters per token)."""
        if not text:
            return 0
        return math.ceil(len(text) / 4)

    def calculate_prompt_budget(self, current_prompt_tokens: int) -> Dict[str, int]:
        available = self.max_context_tokens - self.reserved_output_tokens
        remaining = max(0, available - current_prompt_tokens)
        return {
            "max_context": self.max_context_tokens,
            "reserved_output": self.reserved_output_tokens,
            "available_for_prompt": available,
            "current_prompt_tokens": current_prompt_tokens,
            "remaining_budget": remaining,
        }


class ConversationSummarizer:
    """Generates concise executive summaries for long conversation threads."""

    @staticmethod
    def generate_summary(conversation: Conversation, messages: List[ChatMessage]) -> str:
        if not messages:
            return conversation.summary or ""
        
        user_prompts = [m.content for m in messages if m.role == MessageRole.USER.value]
        last_prompts = user_prompts[-3:] if len(user_prompts) >= 3 else user_prompts
        
        summary_topics = ", ".join([p[:40].strip() for p in last_prompts])
        summary = (
            f"Executive Summary ({len(messages)} messages): Conversation focused on topics including: {summary_topics}. "
            f"Key goal: {conversation.title}."
        )
        return summary[:500]


class ContextWindowManager:
    """Maintains ordered conversation history and trims oldest messages to fit token budget."""

    def __init__(self, budget_manager: Optional[TokenBudgetManager] = None):
        self.budget_manager = budget_manager or TokenBudgetManager(
            max_context_tokens=settings.MAX_CONTEXT_TOKENS
        )

    def prepare_context_window(
        self,
        system_prompt: str,
        summary: Optional[str],
        messages: List[ChatMessage],
        current_prompt: str,
        knowledge_context: Optional[str] = None,
    ) -> Tuple[List[Dict[str, str]], int]:
        """
        Trims message history to ensure total prompt tokens stay within budget.
        System prompt, summary, knowledge context, and current prompt are strictly preserved.
        """
        system_tokens = TokenBudgetManager.estimate_tokens(system_prompt)
        summary_tokens = TokenBudgetManager.estimate_tokens(summary or "")
        knowledge_tokens = TokenBudgetManager.estimate_tokens(knowledge_context or "")
        prompt_tokens = TokenBudgetManager.estimate_tokens(current_prompt)

        base_tokens = system_tokens + summary_tokens + knowledge_tokens + prompt_tokens
        available_history_budget = (
            self.budget_manager.max_context_tokens
            - self.budget_manager.reserved_output_tokens
            - base_tokens
        )

        formatted_messages: List[Dict[str, str]] = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        if summary:
            formatted_messages.append({"role": "system", "content": f"[Conversation Summary]: {summary}"})
        if knowledge_context:
            formatted_messages.append({
                "role": "system",
                "content": f"[Enterprise Knowledge Engine Retracted Sources]:\n{knowledge_context}\n\nPlease use the above sources to ground your response and reference sources accurately.",
            })

        # Process messages in reverse (newest first) to preserve latest context
        included_history: List[Dict[str, str]] = []
        accumulated_tokens = 0

        for msg in reversed(messages):
            msg_tokens = TokenBudgetManager.estimate_tokens(msg.content)
            if accumulated_tokens + msg_tokens > available_history_budget:
                logger.info(f"Context window threshold reached. Trimmed history at message [{msg.id}]")
                break
            
            included_history.insert(0, {"role": msg.role, "content": msg.content})
            accumulated_tokens += msg_tokens

        formatted_messages.extend(included_history)
        formatted_messages.append({"role": "user", "content": current_prompt})

        total_prompt_tokens = base_tokens + accumulated_tokens
        return formatted_messages, total_prompt_tokens


class MemoryManager:
    """Short-term and long-term memory coordinator."""

    def __init__(self):
        self.budget_manager = TokenBudgetManager(max_context_tokens=settings.MAX_CONTEXT_TOKENS)
        self.summarizer = ConversationSummarizer()
        self.window_manager = ContextWindowManager(self.budget_manager)

    def prepare_memory_context(
        self,
        conversation: Conversation,
        messages: List[ChatMessage],
        current_prompt: str,
        system_prompt: str = "You are NeuroDesk AI, an intelligent workspace assistant.",
        knowledge_context: Optional[str] = None,
        citations: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        # Check if auto-summarization is triggered (> 10 messages or > 2000 tokens)
        total_tokens = sum(TokenBudgetManager.estimate_tokens(m.content) for m in messages)
        summary = conversation.summary
        
        if total_tokens > 2000 and not summary:
            summary = self.summarizer.generate_summary(conversation, messages)
            logger.info(f"Auto-generated conversation summary for conversation [{conversation.id}]")

        formatted_context, prompt_token_count = self.window_manager.prepare_context_window(
            system_prompt=system_prompt,
            summary=summary,
            messages=messages,
            current_prompt=current_prompt,
            knowledge_context=knowledge_context,
        )

        budget_info = self.budget_manager.calculate_prompt_budget(prompt_token_count)

        return {
            "formatted_messages": formatted_context,
            "prompt_tokens": prompt_token_count,
            "summary": summary,
            "budget_info": budget_info,
            "knowledge_context": knowledge_context,
            "citations": citations or [],
            "hooks": {
                "assets": [],
                "metadata": [],
                "retriever": "KnowledgeEngine",
                "workspace_memory": None,
            },
        }


memory_manager = MemoryManager()
