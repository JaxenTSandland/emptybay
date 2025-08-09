from pydantic import BaseModel

class RegisterIn(BaseModel):
    username: str
    password: str

class LoginIn(BaseModel):
    username: str
    password: str

class ResetRequestIn(BaseModel):
    username: str

class ResetConfirmIn(BaseModel):
    username: str
    token: str
    new_password: str

class BulkCreateIn(BaseModel):
    usernames: list[str]
    length: int = 12
    overwrite: bool = False