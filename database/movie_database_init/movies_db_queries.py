from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Movie, MovieGenre, Genre


async def insert_genre(session: AsyncSession, genre_info: dict):
    obj = Genre(
        id = genre_info["id"],
        genre_name = genre_info["name"]
    )
    session.add(obj)
    await session.commit()


async def insert_movie(session: AsyncSession, movie_info: dict):
    obj = Movie(
        id = movie_info["id"],
        title = movie_info["title"],
        description = movie_info["description"],
        release_year = movie_info["release_year"],
        rating = movie_info["rating"],
        poster = movie_info["poster_url"]
        )
    session.add(obj)
    await insert_movie_genres(session, movie_info["id"], movie_info["genres"])
    await session.commit()


async def insert_movie_genres(session: AsyncSession, movie_id: int, movie_genres: list):
    for genre in movie_genres:
        obj = MovieGenre(
            movie_id = movie_id,
            genre_id = genre,
            )
        session.add(obj)
        await session.commit()
