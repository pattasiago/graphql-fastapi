# GraphQL + FastAPI Test Application

This project is a test application built with **GraphQL** using **FastAPI** as the framework. It demonstrates the use of FastAPI with GraphQL queries, integrated with a PostgreSQL database.

## Features

- FastAPI integrated with GraphQL (via Strawberry)
- Query support
- PostgreSQL database integration

## Getting Started

### Prerequisites

Ensure you have the following installed:

- Docker
- Docker Compose

### Running the Application

1. **Clone the repository**:

    ```bash
    git clone https://github.com/pattasiago/graphql-fastapi.git
    cd graphql-fastapi
    ```

2. **Run the application using Docker Compose**:

    ```bash
    docker-compose up --build
    ```

    This command builds the Docker image and starts the application and PostgreSQL database in containers.

3. **Access the application**:

    Once the containers are up, you can access the GraphQL Playground by navigating to [http://localhost:5433/graphql](http://localhost:5433/graphql).

## GraphQL API Overview

The application exposes a simple GraphQL API with the following schema:

### Queries

- `getUsers`: Fetches a list of users
- `getPosts(userId: ID!)`: Fetches posts or specific posts by user ID
