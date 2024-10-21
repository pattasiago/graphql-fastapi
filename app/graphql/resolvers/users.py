
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.graphql.schemas import UserSchema, PostSchema
from app.models import User

class UserResolver:
    def __init__(self, db: Session):
        self.db = db

    def execute(self, info) -> List[UserSchema]:
        load_posts = self._should_load_posts(info.selected_fields[0].selections)
        query = self._build_query(load_posts)
        users = query.all()
        return [
            UserSchema(
                id=user.id,
                name=user.name,
                email=user.email,
                posts=[
                    PostSchema(id=post.id, title=post.title, 
                               content=post.content, owner=[])
                    for post in user.posts
                ] if load_posts else []
            )
            for user in users
        ]
    
    def _build_query(self, load_posts) -> Session:
        users = self.db.query(User)

        if load_posts:
            users = users.options(joinedload(User.posts, innerjoin=True))
            
        return users

    def _should_load_posts(self, selections) -> bool:
        owner_fields = list(filter(lambda x: x.name == "posts", selections))
        if owner_fields:
            return True
        return False
