from sqlalchemy import Float, ForeignKey, Integer, String, BigInteger, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger)


class Genre(Base):
    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    genre_name: Mapped[str] = mapped_column(String(30))


class Movie(Base):
    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    title: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(Text)
    release_year: Mapped[int] = mapped_column(Integer)
    rating: Mapped[float] = mapped_column(Float)
    poster: Mapped[str] = mapped_column(String(200))


class MovieGenre(Base):
    __tablename__ = "movie_genres"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"))
    genre_id: Mapped[int] = mapped_column(ForeignKey("genres.id", ondelete="CASCADE"))

    movie: Mapped["Movie"] = relationship(backref = "movie_genres")
    genre: Mapped["Genre"] = relationship(backref = "movie_genres")


class UserFilter(Base):
    __tablename__ = "users_filters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id", ondelete="CASCADE"),)
    rating_lower_border: Mapped[float] = mapped_column(Float)
    year_lower_border: Mapped[int] = mapped_column(Integer)
    year_upper_border: Mapped[int] = mapped_column(Integer)
    genre_id: Mapped[int] = mapped_column(ForeignKey("genres.id", ondelete="CASCADE"))

    user: Mapped["User"] = relationship(backref="users_filters")
    genre: Mapped["Genre"] = relationship(backref = "users_filters")


class Favourite(Base):
    __tablename__ = "favourites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.tg_id", ondelete="CASCADE"))
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"))

    user: Mapped["User"] = relationship(backref = "favourites")
    movie: Mapped["Movie"] = relationship(backref = "favourites")
