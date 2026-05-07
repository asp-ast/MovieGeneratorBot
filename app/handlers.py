from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from app.funcs import get_filters_message
from database.orm_queries import orm_add_to_favourites, orm_add_unique_user, orm_del_from_favourites, orm_generate_random_movie, orm_get_favourites, orm_get_movie, orm_get_standard_filters, orm_get_user_filters, orm_is_favourite, orm_set_user_filters
import app.keyboards as kb

router = Router()


class UsrFilters(StatesGroup):
    menu = State()
    rating_filter = State()
    year_lower_filter = State()
    year_upper_filter = State()
    genre_filter = State()


@router.message(Command("start"))
async def cmd_start(message: Message, session: AsyncSession):
    await orm_add_unique_user(session, message.from_user.id)
    await message.answer('Главное меню:', reply_markup = kb.main_kb)


@router.message(F.text == "🎲Сгенерировать случайный фильм")
async def generate_movie(message: Message, session: AsyncSession, state: FSMContext):
    await state.clear()
    movie_info = await orm_generate_random_movie(session, message.from_user.id)
    if not movie_info:
        await message.answer("По заданным фильтрам фильмов не найдено", reply_markup=kb.main_kb)
        return
    movie = movie_info["movie"]
    genres = ", ".join(movie_info["genres"])
    is_favourite = await orm_is_favourite(session, message.from_user.id, movie.id)
    await message.answer_photo(
        movie.poster,
        caption = f"{movie.title}\n\n{movie.description}\n\nЖанры: {genres}\nГод выпуска: {movie.release_year}\nРейтинг: {movie.rating}",
        reply_markup = await kb.fav_btn(movie.id, is_favourite)
    )


@router.message(F.text == "⚙️Фильтры")
async def set_filters(message: Message, session: AsyncSession, state: FSMContext):
    await state.clear()
    message_text = await get_filters_message(session, message.from_user.id)
    await message.answer(message_text, reply_markup=kb.filters_kb)


@router.callback_query(F.data == "no_filters")
async def reset_filters(callback: CallbackQuery, session: AsyncSession):
    standard_filters = await orm_get_standard_filters(session)
    await orm_set_user_filters(session, callback.from_user.id, standard_filters)
    message_text = await get_filters_message(session, callback.from_user.id)
    await callback.answer("Фильтры сброшены")
    await callback.message.edit_text(message_text, reply_markup=kb.filters_kb)


@router.callback_query(F.data == "action_cancel")
async def action_cancel(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    await state.clear()
    message_text = await get_filters_message(session, callback.from_user.id)
    await callback.answer()
    await callback.message.edit_text(message_text, reply_markup=kb.filters_kb)


@router.callback_query(F.data == "rating_filter", StateFilter(None))
async def start_rating_filter(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Введите нижнюю границу рейтинга(число от 1 до 10): ", reply_markup=kb.cancel_btn)
    await state.set_state(UsrFilters.rating_filter)
    await callback.answer()


@router.message(UsrFilters.rating_filter)
async def set_rating_filter(message: Message, state: FSMContext, session: AsyncSession):
    try:
        rating = float(message.text)
        if not 1 <= rating <= 10:
            raise ValueError
    except ValueError:
        await message.answer("Введите число от 1 до 10!", reply_markup=kb.cancel_btn)
        return

    user_id = message.from_user.id
    current_filters = await orm_get_user_filters(session, user_id)
    current_filters["rating_lower_border"] = rating
    await orm_set_user_filters(session, user_id, current_filters)
    await state.clear()
    await message.answer("Фильтр по рейтингу обновлен")
    message_text = await get_filters_message(session, message.from_user.id)
    await message.answer(message_text, reply_markup=kb.filters_kb)


@router.callback_query(F.data == "year_filter", StateFilter(None))
async def start_year_filter(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Введите нижнюю границу года выпуска(четырехзначное число от 1902 до 2026): ", reply_markup=kb.cancel_btn)
    await state.set_state(UsrFilters.year_lower_filter)
    await callback.answer()


@router.message(UsrFilters.year_lower_filter)
async def set_year_lower_filter(message: Message, state: FSMContext):
    try:
        year_lower_filter = int(message.text)
        if not 1902 <= year_lower_filter <= 2026:
            raise ValueError
    except ValueError:
        await message.answer("Введите четырехзначное число от 1902 до 2026!", reply_markup=kb.cancel_btn)
        return

    await state.update_data(year_lower_filter = int(message.text))
    await message.answer("Введите верхнюю границу года выпуска(четырехзначное число от 1902 до 2026 большее или равное нижней границе): ", reply_markup=kb.cancel_btn)
    await state.set_state(UsrFilters.year_upper_filter)


@router.message(UsrFilters.year_upper_filter)
async def set_year_upper_filter(message: Message, state: FSMContext, session: AsyncSession):
    try:
        year_upper_filter = int(message.text)
        data = await state.get_data()
        year_lower_filter = data.get("year_lower_filter")
        if not 1902 <= year_upper_filter <= 2026 or year_upper_filter < year_lower_filter:
            raise ValueError
    except ValueError:
        await message.answer("Введите четырехзначное число от 1902 до 2026 большее или равное нижней границе!", reply_markup=kb.cancel_btn)
        return

    user_id = message.from_user.id
    current_filters = await orm_get_user_filters(session, user_id)
    current_filters["year_lower_border"] = year_lower_filter
    current_filters["year_upper_border"] = year_upper_filter

    await orm_set_user_filters(session, user_id, current_filters)
    await state.clear()
    await message.answer("Фильтр по годам обновлен")
    message_text = await get_filters_message(session, message.from_user.id)
    await message.answer(message_text, reply_markup=kb.filters_kb)


@router.callback_query(F.data == "genre_filter", StateFilter(None))
async def start_genre_filter(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await state.set_state(UsrFilters.genre_filter)
    await callback.message.edit_text("Выберите жанр:", reply_markup=await kb.genres_kb(session))
    await callback.answer()


@router.callback_query(UsrFilters.genre_filter, F.data.startswith("genre_filter_"))
async def set_genre_filter(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    genre_id = int(callback.data.split("_")[-1])
    user_id = callback.from_user.id
    current_filters = await orm_get_user_filters(session, user_id)
    current_filters["genre_id"] = genre_id
    await orm_set_user_filters(session, user_id, current_filters)
    await state.clear()
    await callback.answer("Фильтр по жанру обновлен")
    message_text = await get_filters_message(session, callback.from_user.id)
    await callback.message.edit_text(message_text, reply_markup=kb.filters_kb)


@router.callback_query(F.data.startswith("fav_add_"))
async def add_to_fav(callback: CallbackQuery, session: AsyncSession):
    movie_id = int(callback.data.split("_")[-1])
    await orm_add_to_favourites(session, callback.from_user.id, movie_id)
    is_fav = True
    await callback.message.edit_reply_markup(reply_markup= await kb.fav_btn(movie_id, is_fav))


@router.callback_query(F.data.startswith("fav_del_page_"))
async def del_fav_from_paginator(callback: CallbackQuery, session: AsyncSession):
    data = callback.data.split("_")
    movie_id = int(data[-2])
    current_index = int(data[-1])
    user_id = callback.from_user.id

    await orm_del_from_favourites(session, user_id, movie_id)
    favs = await orm_get_favourites(session, user_id)

    if not favs:
        await callback.message.delete()
        await callback.message.answer("Список избранного пуст", reply_markup=kb.main_kb)
        await callback.answer("Удалено из избранного")
        return
    
    new_len = len(favs)
    new_index = current_index if current_index < new_len else new_len - 1
    movie_id_new = favs[new_index].movie_id
    movie_info = await orm_get_movie(session, movie_id_new)
    movie = movie_info["movie"]
    genres = ", ".join(movie_info["genres"])

    await callback.message.delete()

    await callback.bot.send_photo(
        callback.message.chat.id,
        movie.poster,
        caption = f"{movie.title}\n\n{movie.description}\n\nЖанры: {genres}\nГод выпуска: {movie.release_year}\nРейтинг: {movie.rating}",
        reply_markup = await kb.favs_paginator_kb(new_index, new_len, movie_id_new)
    )

    await callback.answer("Удалено из избранного")


@router.callback_query(F.data.startswith("fav_del_"))
async def del_from_fav(callback: CallbackQuery, session: AsyncSession):
    movie_id = int(callback.data.split("_")[-1])
    await orm_del_from_favourites(session, callback.from_user.id, movie_id)
    is_fav = False
    await callback.message.edit_reply_markup(reply_markup= await kb.fav_btn(movie_id, is_fav))


@router.message(F.text == "⭐️Избранное")
async def see_favs(message: Message, session: AsyncSession):
    user_id = message.from_user.id
    favs = await orm_get_favourites(session, user_id)
    if not favs:
        await message.answer("Список избранного пуст", reply_markup=kb.main_kb)
        return

    movie_id = favs[0].movie_id
    movie_info = await orm_get_movie(session, movie_id)
    movie = movie_info["movie"]
    genres = ", ".join(movie_info["genres"])
    await message.answer_photo(
        movie.poster,
        caption = f"{movie.title}\n\n{movie.description}\n\nЖанры: {genres}\nГод выпуска: {movie.release_year}\nРейтинг: {movie.rating}",
        reply_markup = await kb.favs_paginator_kb(0, len(favs), movie_id)
    )


@router.callback_query(F.data == "no_action")
async def no_action(callback: CallbackQuery):
    await callback.answer()


@router.callback_query(F.data.startswith("fav_page_"))
async def change_fav_page(callback: CallbackQuery, session: AsyncSession):
    index = int(callback.data.split("_")[-1])
    user_id = callback.from_user.id
    favs = await orm_get_favourites(session, user_id)
    if not favs or index >= len(favs):
        await callback.answer("Выход за пределы списка")
        return

    await callback.message.delete()
    movie_id = favs[index].movie_id
    movie_info = await orm_get_movie(session, movie_id)
    movie = movie_info["movie"]
    genres = ", ".join(movie_info["genres"])
    await callback.bot.send_photo(
        callback.message.chat.id,
        movie.poster,
        caption = f"{movie.title}\n\n{movie.description}\n\nЖанры: {genres}\nГод выпуска: {movie.release_year}\nРейтинг: {movie.rating}",
        reply_markup = await kb.favs_paginator_kb(index, len(favs), movie_id)
    )

    await callback.answer()


@router.callback_query(F.data == "go_main")
async def go_main(callback: CallbackQuery):
    await callback.answer("Меню:")
    await callback.message.delete()
    await callback.message.answer('Главное меню:', reply_markup = kb.main_kb)
