from pydantic import BaseModel, Field


class UserInfoInJWT(BaseModel):
    """User information to be wrapped inside the jwt token that will be passed to FE"""

    username: str
    role: str


class UserLoginBody(BaseModel):
    """Data body when FE call login to BE to get token"""

    username: str = Field(..., description="Username to login", min_length=1)
    password: str = Field(..., description="Password to login", min_length=1)
