from pydantic import BaseModel, Field


class DevLoginRequest(BaseModel):
    user_id: int = Field(ge=1)


class AuthSessionRead(BaseModel):
    user_id: int
    student_profile_id: int