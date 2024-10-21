
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.graphql.schemas import PostSchema, UserSchema
from app.models import Post

class PostResolver:
    def __init__(self, db: Session):
        self.db = db

    def get_posts(self, info, user_id: Optional[int] = None) -> List[PostSchema]:
        load_owner = self._should_load_owner(info.selected_fields[0].selections)
        query = self._build_query(load_owner, user_id)
        posts = query.all()
        return [
            PostSchema(
                id=post.id,
                title=post.title,
                content=post.content,
                owner=UserSchema(
                    id=post.user_id,
                    name=post.owner.name if load_owner else None,
                    email=post.owner.email if load_owner else None,
                    posts=None
                )
            )
            for post in posts
        ]

    def _build_query(self, load_owner: bool, user_id: Optional[int]) -> Session:
        query = self.db.query(Post)
        if user_id:
            query = query.filter(Post.user_id == user_id)

        if load_owner:
            query = query.options(joinedload(Post.owner, innerjoin=True))

        return query

    def _should_load_owner(self, selections) -> bool:
        owner_fields = list(filter(lambda x: x.name == "owner", selections))
        if owner_fields:
            owner_fields_names = [f.name for f in owner_fields[0].selections]
            return len(owner_fields_names) > 1
        return False
