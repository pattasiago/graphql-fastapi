from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class UserPlan(Base):
    __tablename__ = 'UserPlans'

    # Definindo as colunas da tabela UserPlans
    id = Column("Id", Integer, primary_key=True)  # Chave primária
    
    #No foreign key usar nome da tabela ao invés da classe Python
    userId = Column("UserId", Integer, ForeignKey('Users.Id'), nullable=False)
    planId = Column("PlanId", Integer, ForeignKey('Plans.Id'), nullable=False)


class User(Base):
    __tablename__ = 'Users'
    
    id = Column("Id", Integer, primary_key=True)
    name = Column("Name", String(100), nullable=False)
    email = Column("Email", String(100), unique=True, nullable=False)
    createdAt = Column("CreatedAt", TIMESTAMP)

    posts = relationship("Post", back_populates="owner", lazy='noload')
    #No secondary usar nome da tabela ao invés da classe Python
    plan = relationship("Plan", secondary="UserPlans", back_populates="user", lazy='noload')


class Post(Base):
    __tablename__ = 'Posts'

    id = Column("Id", Integer, primary_key=True)  # Chave primária
    title = Column("Title", String(200))  # Título do post
    content = Column("Content")  # Conteúdo do post
    createdAt = Column("CreatedAt", TIMESTAMP)
    userId = Column("UserId", Integer, ForeignKey('Users.Id'), nullable=False)

    owner = relationship("User", back_populates="posts", lazy='noload')


class Plan(Base):
    __tablename__ = 'Plans'

    # Definindo as colunas da tabela UserPlans
    id = Column("Id", Integer, primary_key=True)  # Chave primária
    name = Column("PlanName", String(50))  # Título do post
    
    user = relationship("User", secondary="UserPlans", back_populates="plan", lazy='noload')