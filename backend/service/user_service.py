from backend.models import Note, User
from backend.crud.crud import*
from backend.schemas import UserLoginSchema, UserRegisterSchema
from pydantic import ValidationError


def check_user(username):
    return User.query.filter_by(username=username).first() is not None


def create_user(username:str, email:str, password:str):
        try:
            valid = UserRegisterSchema(username=username, email=email,password=password)
        except ValidationError as e:
            return 
        if check_user(valid.username):

            raise ValueError("User already exists")
        else:
            user = User(username=valid.username, email=valid.email)
            user.set_password(valid.password)
            crud_reg(user)
            return user
def login_user(username:str, password:str):
        
        try:
            valid = UserLoginSchema(username=username, password=password)
        except ValidationError as e:
            return None


        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            return user

        return None