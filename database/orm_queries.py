from sqlalchemy import asc, delete, desc, func, select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Favourite, Genre, Movie, MovieGenre, User, UserFilter


async def orm_get_movie_genres(session: AsyncSession, movie_id: int):
    movie_genre_rows = await session.execute(
        select(MovieGenre)
        .where(MovieGenre.movie_id == movie_id)
        .options(selectinload(MovieGenre.genre))
    )

    return [
        movie_genre_row.genre.genre_name
        for movie_genre_row in movie_genre_rows.scalars()
    ]


async def orm_get_standard_filters(session: AsyncSession):
    rating_lower_border = (
        await session.scalar(select(Movie).order_by(asc(Movie.rating)).limit(1))
    ).rating
    year_lower_border = (
        await session.scalar(select(Movie).order_by(asc(Movie.release_year)).limit(1))
    ).release_year
    year_upper_border = (
        await session.scalar(select(Movie).order_by(desc(Movie.release_year)).limit(1))
    ).release_year
    genre_id = -1

    result = {
        "rating_lower_border": rating_lower_border,
        "year_lower_border": year_lower_border,
        "year_upper_border": year_upper_border,
        "genre_id": genre_id,
    }

    return result


async def orm_set_user_filters(session: AsyncSession, user_id: int, filters: dict):
    query = update(UserFilter).where(UserFilter.user_id == user_id).values(
        rating_lower_border=filters["rating_lower_border"],
        year_lower_border=filters["year_lower_border"],
        year_upper_border=filters["year_upper_border"],
        genre_id=filters["genre_id"],
    )

    await session.execute(query)
    await session.commit()


async def orm_add_unique_user(session: AsyncSession, tg_id):
    user = await session.scalar(select(User).where(User.tg_id == tg_id))

    if not user:
        session.add(User(tg_id=tg_id))

        standard_filters = await orm_get_standard_filters(session)
        session.add(
            UserFilter(
                user_id=tg_id,
                rating_lower_border=standard_filters["rating_lower_border"],
                year_lower_border=standard_filters["year_lower_border"],
                year_upper_border=standard_filters["year_upper_border"],
                genre_id=standard_filters["genre_id"],
            )
        )
        await session.commit()


async def orm_get_user_filters(session: AsyncSession, user_id: int):
    user_filters_data = await session.scalar(
        select(UserFilter).where(UserFilter.user_id == user_id)
    )
    result = {
        "rating_lower_border": user_filters_data.rating_lower_border,
        "year_lower_border": user_filters_data.year_lower_border,
        "year_upper_border": user_filters_data.year_upper_border,
        "genre_id": user_filters_data.genre_id,
    }

    return result


async def orm_generate_random_movie(session: AsyncSession, user_id: int):
    user_filters = await orm_get_user_filters(session, user_id)
    if user_filters["genre_id"] != -1:
        query = (
            select(Movie)
            .join(MovieGenre)
            .where(
                MovieGenre.genre_id == user_filters["genre_id"],
                Movie.rating >= user_filters["rating_lower_border"],
                Movie.release_year >= user_filters["year_lower_border"],
                Movie.release_year <= user_filters["year_upper_border"],
            )
            .order_by(func.random())
            .limit(1)
        )
    else:
        query = (
            select(Movie)
            .where(
                Movie.rating >= user_filters["rating_lower_border"],
                Movie.release_year >= user_filters["year_lower_border"],
                Movie.release_year <= user_filters["year_upper_border"],
            )
            .order_by(func.random())
            .limit(1)
        )
    movie = await session.scalar(query)
    if not movie:
        return None
    genres = await orm_get_movie_genres(session, movie.id)
    movie_info = {"movie": movie, "genres": genres}

    return movie_info


async def orm_get_movie(session: AsyncSession, movie_id: int):
    movie = await session.scalar(select(Movie)
                                 .where(Movie.id == movie_id))
    genres = await orm_get_movie_genres(session, movie.id)
    movie_info = {"movie": movie, "genres": genres}

    return movie_info


async def orm_get_genres_list(session: AsyncSession):
    genre_rows = await session.scalars(select(Genre))

    return genre_rows.all()


async def orm_is_favourite(session: AsyncSession, user_id: int, movie_id: int):
    already_exists = await session.scalar(
        select(Favourite)
        .where(Favourite.user_id == user_id,
               Favourite.movie_id == movie_id)
    )

    if already_exists:
        return True
    return False


async def orm_add_to_favourites(session: AsyncSession, user_id: int, movie_id: int):
    session.add(Favourite(
        user_id = user_id,
        movie_id = movie_id
    ))
    await session.commit()


async def orm_del_from_favourites(session: AsyncSession, user_id: int, movie_id: int):
    await session.execute(delete(Favourite).where(
        Favourite.user_id == user_id,
        Favourite.movie_id == movie_id
    ))
    await session.commit()


async def orm_get_favourites(session: AsyncSession, user_id: int):
    favourites = await session.scalars(
        select(Favourite)
        .where(Favourite.user_id == user_id)
    )

    return favourites.all()

# async def orm_count_favourites(session: AsyncSession, user_id: int):
#     favs_amount = await session.scalar(select(func.count())
#                                        .select_from(Favourite)
#                                        .where(Favourite.user_id == user_id))
    
#     return favs_amount
