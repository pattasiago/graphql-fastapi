import strawberry
from app.graphql.schemas import PostSchema, UserSchema
from app.graphql.resolvers.posts import PostResolver
from app.graphql.resolvers.users import UserResolver
from typing import List, Optional


@strawberry.type
class Query:
    @strawberry.field
    async def get_users(self,  info) -> List[UserSchema]:
        db = info.context["db"]
        posts = UserResolver(db)
        return posts.get_users(info)
     
    @strawberry.field
    async def get_posts(self, info, user_id: Optional[int] = None) -> List[PostSchema]:
        db = info.context["db"]
        posts = PostResolver(db)
        return posts.get_posts(info, user_id)