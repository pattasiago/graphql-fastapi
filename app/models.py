from sqlalchemy import MetaData, Table, Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship, column_property
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base
from app.database import engine


Base = declarative_base()
# MetaData para refletir o esquema
metadata = MetaData()
# Refletir tabelas do banco de dados
metadata.reflect(engine)


class User(Base):
    __tablename__ = 'users'

    # Refletir colunas automaticamente
    __table__ = Table(__tablename__, metadata, autoload_with=engine)
    
    # Alias para a coluna 'created_at', acessível como 'createdAt'
    createdAt = column_property(__table__.c.created_at)

    posts = relationship("Post", back_populates="owner", lazy='joined')


class Post(Base):
    __tablename__ = 'posts'

    __table__ = Table(__tablename__, metadata, autoload_with=engine)

    createdAt = column_property(__table__.c.created_at)
    owner = relationship("User", back_populates="posts", lazy='joined')
