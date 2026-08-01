from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel

T = TypeVar("T")


class ResponseWrapper(BaseModel, Generic[T]):
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[T] = None


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    details: Optional[Any] = None
