# MovieGeneratorBot

## Описание
Telegram-бот, генерирующий случайный фильм с возможностью задать пользовательские фильтры выбора фильма и добавления фильмов в избранное. Бот построен aiogram3 с использованием SQLAlchemy2 и aiosqlite. Данные о фильмах загружаются в базу данных автоматически при первом запуске программы при помощи библиотеки requests через обращение к API сайта TMDB(The Movie Database).

---

## Возможности
- **Генерация случайного фильма** - бот присылает пользователю информацию(постер, название, описание, жанры, год выпуска, рейтинг) о случайном фильме с учетом пользовательских фильтров. Генерация происходит с помощью функции orm_generate_random_movie, которая выполняет select запрос в базу данных для получаения случайного фильма и возвращает информацию о нем.
- **Фильтры** - присутствует возможность задать фильтры и сбросить их до стандартных, фильмы будут выбираться согласно этим фильтрам. Реализовано при помощи работы с состояниями FSM.
- **Избранное** - присутствует возможность добавления и удаления фильмов из избранного, а так же просмотра списка избранных фильмов, реализованного при помощи клавиатры с пагинацией.
- **Автоматическая регистрация пользователей** - при первом запуске бота пользователем, информация о нем(его уникальный telegram id) попадает в базу данных с информацией и пользователях.
- **Заполнение базы данных фильмами** - если база данных еще не создана, бот загружает информацию о 1000 фильмов при помощи запросов к API сайта TMDB.

---

## Демонстрация работы бота
#### Генерация случайного фильма
<img width="800" alt="movie_bot_screenshot1" src="https://github.com/user-attachments/assets/96a26f58-b178-4520-bab2-2603ac932553" />

---

#### Демонстрация главной клавиатуры и возможности добавить фильм в избранное
<img width="600" alt="movie_bot_screenshot2" src="https://github.com/user-attachments/assets/a248777f-4cdd-40a5-a406-fff4f06e7d43" />

---

#### Меню фильтров
<img width="600" alt="movie_bot_screenshot3" src="https://github.com/user-attachments/assets/96d29a95-5df9-4bd2-88da-2e4bb3c5bde8" />

---

#### Выставление фильтра по рейтингу и его валидация
<img width="600" alt="movie_bot_screenshot4" src="https://github.com/user-attachments/assets/f5027585-b721-43e0-8ee6-6b4f14bac700" />

---

#### Страница выбора фильтра по жанру
<img width="600" alt="movie_bot_screenshot5" src="https://github.com/user-attachments/assets/5d9e7a5d-f1a7-4d47-80d5-36d260ac64f0" />

---

#### Выставление фиьтра по году и проверка, что фильмы с заданными жанрами существуют
<img width="600" alt="movie_bot_screenshot6" src="https://github.com/user-attachments/assets/f329b1b5-5153-4247-ad54-1dc85503a2e7" />

---

#### Демонстрация вкладки избранное
<img width="600" alt="movie_bot_screenshot7" src="https://github.com/user-attachments/assets/cd63783e-2d04-4d05-b27d-94f225129f55" />
<img width="600" alt="movie_bot_screenshot8" src="https://github.com/user-attachments/assets/36596f93-fcd6-4b4b-a59f-5fe8e03d0aaf" />

---

## Установка и запуск

#### 1. Клонирование репозитория
```
git clone git@github.com:asp-ast/MovieGeneratorBot.git
cd MovieGeneratorBot
```

#### 2. Виртуальное окружение и зависимости
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

#### 3. Конфиурация
создайте в корне проекта файл .env со следующими константами:
```
TOKEN=...
API_TOKEN=...
PROXY_URL=socks5://ip-адрес:порт
DB_LITE=sqlite+aiosqlite:///movie_database.db
```
- TOKEN - токен для телеграм бота
- API_TOKEN - API ключ для доступа к TMDB
- PROXY_URL - прокси адрес для обхода блокировки телеграм в РФ
- DB_LITE - путь к файлу базы данных(оставить без изменений)

#### 4. Запуск
```
python main.py
```


