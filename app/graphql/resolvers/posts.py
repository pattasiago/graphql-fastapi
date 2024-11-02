
from sqlalchemy.orm import Session
from typing import List, Optional
from app.graphql.resolvers.base_resolver import BaseResolver
from app.graphql.schemas import PostSchema
from app.graphql.inputs import LogicalFilterInput
from app.graphql.helper.filters import apply_filters
from app.models import Post

class PostResolver(BaseResolver):
    def __init__(self, db: Session):
        self.db = db

    def get_posts(self, info, filter: Optional[LogicalFilterInput]) -> List[PostSchema]:
        query = self.db.query(Post)
        requested_fields = self.get_requested_fields(info)
        posts = apply_filters(query, filter, Post, requested_fields)
        posts = posts.all()
        return [
            PostSchema.marshal(post)
            for post in posts
        ]

