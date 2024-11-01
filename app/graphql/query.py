import strawberry
from app.graphql.schemas import UserSchema, PostSchema
from app.graphql.inputs import LogicalFilterInput
from app.graphql.resolvers.posts import PostResolver
from app.graphql.resolvers.users import UserResolver
from typing import List, Optional


@strawberry.type
class Query:
    @strawberry.field
    async def get_users(self,  info, filter: Optional[LogicalFilterInput] = None) -> List[UserSchema]:
        db = info.context["db"]
        users = UserResolver(db)
        return users.get_users(info, filter)
     
    @strawberry.field
    async def get_posts(self, info, filter: Optional[LogicalFilterInput] = None) -> List[PostSchema]:
        db = info.context["db"]
        posts = PostResolver(db)
        return posts.get_posts(info, filter)