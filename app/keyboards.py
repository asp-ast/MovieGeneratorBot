from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from aiogram.utils.keyboard import InlineKeyboardBuilder

from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_queries import orm_get_genres_list


main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎲Сгенерировать случайный фильм")],
        [KeyboardButton(text="⚙️Фильтры")],
        [KeyboardButton(text="⭐️Избранное")],
    ],
    resize_keyboard=True,
    input_field_placeholder='Меню:'
)

filters_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="по рейтингу", callback_data="rating_filter"),
         InlineKeyboardButton(text="по году", callback_data = "year_filter")],
        [InlineKeyboardButton(text="по жанру", callback_data = "genre_filter")],
        [InlineKeyboardButton(text="Сбросить все фильтры", callback_data="no_filters")],
        [InlineKeyboardButton(text="На главную", callback_data="go_main")]
    ]
)

cancel_btn = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = "❌Отмена", callback_data="action_cancel")]])


async def fav_btn(movie_id: int, is_favourite: bool):
    if is_favourite:
        favourite_btn = InlineKeyboardButton(text = "❌Удалить из избранного", callback_data=f"fav_del_{movie_id}")
    else:
        favourite_btn = InlineKeyboardButton(text = "⭐️Добавить в избранное", callback_data=f"fav_add_{movie_id}")

    return InlineKeyboardMarkup(inline_keyboard=[[favourite_btn]])


async def genres_kb(session: AsyncSession):
    genres_list = await orm_get_genres_list(session)
    keyboard = InlineKeyboardBuilder()

    for genre in genres_list:
        keyboard.add(InlineKeyboardButton(text = genre.genre_name,
                                          callback_data=f"genre_filter_{genre.id}"))
    keyboard.add(InlineKeyboardButton(text="❌Отмена", callback_data="action_cancel"))

    return keyboard.adjust(2).as_markup()


async def favs_paginator_kb(current_index: int, total: int, movie_id: int):
    buttons = []

    if total > 1:
        row = []
        if current_index > 0:
            row.append(InlineKeyboardButton(
                text="◀️Назад",
                callback_data=f"fav_page_{current_index - 1}"))
        
        row.append(InlineKeyboardButton(
            text=f"{current_index + 1}/{total}",
            callback_data="no_action"
        ))

        if current_index < total - 1:
            row.append(InlineKeyboardButton(
                text="Вперед▶️",
                callback_data=f"fav_page_{current_index + 1}"))
        buttons.append(row)
    
    buttons.append([InlineKeyboardButton(text="❌Удалить из избранного", callback_data=f"fav_del_page_{movie_id}_{current_index}")])

    
    buttons.append([InlineKeyboardButton(text="На главную", callback_data="go_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
