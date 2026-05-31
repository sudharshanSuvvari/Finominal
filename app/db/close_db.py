# # app/db/close_db.py

# from app.db.db_connection import engine
# from app.models.base import Base

# async def close_db():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)