import strawberry
from typing import List

@strawberry.type
class PostSchema:
    id: int
    title: str
    content: str
    owner: "UserSchema"


@strawberry.type
class UserSchema:
    id: int
    name: str
    email: str
    posts: List["PostSchema"]