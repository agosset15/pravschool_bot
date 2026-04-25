from typing import Optional

from pydantic import BaseModel

from src.core.enums import UserRole


class UserResponse(BaseModel):
    telegram_id: int
    username: Optional[str]
    referral_code: Optional[str]
    is_blocked: bool

    name: str
    role: UserRole
    grade: str

    is_ns: bool
    is_teacher: bool
    is_parent: bool

    default_child: int
    login: Optional[str]

    schedule_id: Optional[int]


class UserUpdateRequest(BaseModel):
    grade: Optional[str]
    login: Optional[str]
    password: Optional[str]
    default_child: Optional[int]


class UserCreateRequest(BaseModel):
    referral_code: Optional[str]
    is_teacher: bool
    schedule_id: int

    login: Optional[str]
    password: Optional[str]
