import strawberry
from typing import List, Optional
from datetime import datetime
from app import models


@strawberry.type
class PlanSchema:
    id: strawberry.ID
    name: str

    @classmethod
    def marshal(cls, plan: models.Plan) -> "PlanSchema":
        return cls(id=plan.id,
                   name=plan.name)

@strawberry.type
class BasePostSchema:
    id: strawberry.ID
    title: str
    content: str
    created_at: datetime

    @classmethod
    def marshal(cls, post: models.Post) -> "BasePostSchema":
        return cls(id=post.id,
                   title=post.title,
                   content=post.content,
                   created_at=post.createdAt)

@strawberry.type
class PostSchema(BasePostSchema):
    owner: Optional["BaseUserSchema"]
    
    @classmethod
    def marshal(cls, post: models.Post) -> "PostSchema":
        base_instance = BasePostSchema.marshal(post).__dict__
        base_instance.update(
            {"owner": BaseUserSchema.marshal(post.owner)}
        )
        return cls(**base_instance)


@strawberry.type
class BaseUserSchema:
    id: strawberry.ID
    name: str
    email: str
    created_at: datetime
    plan: Optional["PlanSchema"]

    @classmethod
    def marshal(cls, user: models.User) -> "BaseUserSchema":
        return cls(id=user.id,
                   name=user.name,
                   email=user.email,
                   plan=PlanSchema.marshal(user.plan[0]) if user.plan else None,
                   created_at=user.createdAt)

@strawberry.type
class UserSchema(BaseUserSchema):
    posts: Optional[List["BasePostSchema"]]

    @classmethod
    def marshal(cls, user: models.User) -> "UserSchema":
        base_instance = BaseUserSchema.marshal(user).__dict__
        base_instance.update({
            "posts": [BasePostSchema.marshal(post) for post in user.posts]

        })
        return cls(**base_instance)
