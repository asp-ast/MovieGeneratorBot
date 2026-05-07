import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from database.models import Base
from database.movie_database_init.movies_db_queries import insert_movie, insert_genre
from database.movie_database_init.movies_scrapper import scrap_movies, scrap_genres


engine = create_async_engine(os.getenv('DB_LITE'), echo=True)

session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)



async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, checkfirst = True)

    async with session_maker() as session:
        for genre_info in scrap_genres():
            await insert_genre(session, genre_info)
        for movie_info in scrap_movies():
            await insert_movie(session, movie_info)


async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
