from sqlmodel import SQLModel

class SigninRequest(SQLModel):
    username: str
    password: str

class SignupRequest(SQLModel):
    name: str
    username: str
    email: str
    password: str