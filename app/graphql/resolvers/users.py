
from sqlalchemy.orm import Session
from typing import List, Optional
from app.graphql.schemas import UserSchema
from app.graphql.inputs import LogicalFilterInput
from app.graphql.resolvers.base_resolver import BaseResolver
from app.graphql.helper.filters import apply_filters
from app.models import User

class UserResolver(BaseResolver):
    def __init__(self, db: Session):
        self.db = db

    def get_users(self, info, filter: Optional[LogicalFilterInput]) -> List[UserSchema]:
        query = self.db.query(User)
        requested_fields = self.get_requested_fields(info)
        users = apply_filters(query, filter, User, requested_fields)
        users = users.all()
        return [
            UserSchema.marshal(user) for user in users
        ]
