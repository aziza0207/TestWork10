from pydantic import BaseModel, Field
from typing import Optional
from ..utils.enums import ServiceStatus


class ServiceBase(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    status: Optional[ServiceStatus] = ServiceStatus.PENDING
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0)

    class Config:
        from_attributes = True


class ServiceUpdate(BaseModel):
    title: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    priority: Optional[int] = Field(default=None, gt=0)
    status: Optional[ServiceStatus]

    class Config:
        from_attributes = True


class ServiceList(ServiceBase):
    id: int = Field()
