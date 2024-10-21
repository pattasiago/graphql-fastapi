import strawberry
from fastapi import FastAPI, Depends
from strawberry.fastapi import GraphQLRouter
from sqlalchemy.orm import Session
from app.database import get_db
from app.graphql.query import Query


def get_context(db: Session = Depends(get_db)):
    return {"db": db}

app = FastAPI()
schema = strawberry.Schema(query=Query)

# Adicionando a rota GraphQL ao FastAPI
graphql_app = GraphQLRouter(schema, context_getter=get_context)
app.include_router(graphql_app, prefix="/graphql")