from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_queries import orm_get_standard_filters, orm_get_user_filters
from database.models import Genre


async def get_filters_message(session: AsyncSession, user_id: int):
    current_filters = await orm_get_user_filters(session, user_id)
    standard_filters = await orm_get_standard_filters(session)

    message_parts = ["Фильтры:\n"]
    if current_filters["rating_lower_border"] != standard_filters["rating_lower_border"]:
        message_parts.append(f"Минимальный рейтинг: {current_filters["rating_lower_border"]}")
    if (current_filters["year_lower_border"] != standard_filters["year_lower_border"] or
        current_filters["year_upper_border"] != standard_filters["year_upper_border"]):
        message_parts.append(f"Год: от {current_filters['year_lower_border']} до {current_filters["year_upper_border"]}")
    if current_filters["genre_id"] != -1:
        genre = await session.scalar(select(Genre).where(Genre.id == current_filters["genre_id"]))
        message_parts.append(f"Жанр: {genre.genre_name}")

    if len(message_parts) == 1:
        message_text = f"{message_parts[0]}\nФильтры не заданы"
    else:
        message_text = "\n".join(message_parts)

    return message_text



