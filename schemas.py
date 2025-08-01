from pydantic import BaseModel, EmailStr, constr

class UserRegisterSchema(BaseModel):
    email: EmailStr
    username: constr(min_length=3, max_length=50)
    password: constr(min_length=6)

class UserLoginSchema(BaseModel):
    username: constr(min_length=3, max_length=50)
    password: constr(min_length=6)

class NoteSchema(BaseModel):
    title: constr(min_length=1, max_length=100)
    content: str
