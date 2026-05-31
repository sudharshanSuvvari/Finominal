# # app/db/db_connection.py

# from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
# from contextlib import asynccontextmanager
# import app.models

# DATABASE_URL = "sqlite+aiosqlite:///./app.db"

# engine = create_async_engine(
#     DATABASE_URL,
#     echo=False,
#     future=True,
# )

# SessionLocal = async_sessionmaker(
#     bind=engine,
#     class_=AsyncSession,
#     expire_on_commit=False,
# )


# async def get_db():
#     async with SessionLocal() as session:
#         try:
#             yield session
#             await session.commit()
#         except Exception:
#             await session.rollback()
#             raise
#         finally:
#             await session.close()