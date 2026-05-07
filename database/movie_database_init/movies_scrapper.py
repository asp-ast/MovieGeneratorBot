import os
import time
import requests

params = {"language": "ru-RU", "include_image_language": "ru-RU"}

headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {os.getenv("API_TOKEN")}",
}

session = requests.Session()


def scrap_genres():
    genre_list = session.get(
        "https://api.themoviedb.org/3/genre/movie/list", headers=headers, params=params
    ).json()["genres"]
    yield from genre_list


def scrap_movies():
    movie_id = 0
    for page in range(1, 100): #Оставляем запас по страницам, т.к. не все фильмы со страницы обязательно попадут в список(из-за проблем с локализацией фильмы, описание которых не переведено на русский, добавляются с пустым описанием)
        if movie_id >= 1000:
            break

        time.sleep(0.25)
        params["page"] = page
        movie_list = session.get(
            "https://api.themoviedb.org/3/movie/top_rated", headers=headers, params=params
        ).json()["results"]

        for movie in movie_list:
            if movie_id >= 1000:
                break

            if movie["overview"] == "":
                continue

            movie_id += 1
            yield {
                "id": movie_id,
                "title": movie["title"],
                "description": movie["overview"],
                "release_year": movie["release_date"][:4],
                "rating": round(float(movie["vote_average"]), 1),
                "genres": movie["genre_ids"],
                "poster_url": "https://image.tmdb.org/t/p/w1280" + movie["poster_path"],
            }
