
from sqlalchemy.orm import Session
from typing import List, Optional
from app.graphql.schemas import UserSchema
from app.graphql.inputs import LogicalFilterInput
from app.graphql.helper.filters import apply_filters
from app.models import User

class UserResolver():
    def __init__(self, db: Session):
        self.db = db

    def get_users(self, info, filter: Optional[LogicalFilterInput]) -> List[UserSchema]:
        query = self.db.query(User)
        users = apply_filters(query, filter, User)
        users = users.all()
        return [
            UserSchema.marshal(user) for user in users
        ]
