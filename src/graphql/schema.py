"""
GraphQL schema for the Sales Dashboard API.

This module defines the complete schema and context.
"""

import strawberry
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.fastapi import GraphQLRouter

from src.core.database import get_db
from src.graphql.dataloaders import get_dataloaders
from src.graphql.mutations import Mutation
from src.graphql.queries import Query


async def get_context(
    request: Request = None,
):
    """
    Build GraphQL context for each request.

    The context provides:
    - db: Database session
    - dataloaders: DataLoaders for efficient batch loading
    - request: FastAPI request object
    """
    # Get database session
    db_gen = get_db()
    db: AsyncSession = await anext(db_gen)

    try:
        # Create dataloaders
        dataloaders = get_dataloaders(db)

        yield {
            "db": db,
            "dataloaders": dataloaders,
            "request": request,
        }
    finally:
        # Close database session
        await db.close()


# Create schema
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
)


# Create GraphQL router for FastAPI integration
graphql_router = GraphQLRouter(
    schema,
    context_getter=get_context,
)
