CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    user_username TEXT NOT NULL UNIQUE,
    user_password TEXT,
    user_isadmin BOOLEAN
);
CREATE TABLE movies (
    movie_id SERIAL PRIMARY KEY,
    movie_name TEXT NOT NULL UNIQUE,
    movie_year INTEGER NOT NULL,
    movie_runtime INTEGER NOT NULL,
    CHECK (
        movie_year >= 1900 and
        movie_year <= 2099 and
        movie_runtime >= 1 and
        movie_runtime <= 2000 and
        LENGTH(movie_name) >= 1 and
        LENGTH(movie_name) <= 200
    )
);
CREATE TABLE reviews (
    review_id SERIAL PRIMARY KEY,
    review_user_id INTEGER REFERENCES users ON DELETE CASCADE,
    review_movie_id INTEGER REFERENCES movies ON DELETE CASCADE,
    review_date TIMESTAMP WITH TIME ZONE,
    review_text TEXT NOT NULL,
    review_score INTEGER NOT NULL,
    UNIQUE (review_user_id, review_movie_id),
    CHECK (review_score >= 1 AND review_score <= 5 AND LENGTH(review_text) >= 0 AND LENGTH(review_text) <= 600)
);
CREATE TABLE genres (
    genre_id SERIAL PRIMARY KEY,
    genre_name TEXT NOT NULL UNIQUE
);
CREATE TABLE movies_genres (
    movies_genres_movie_id INTEGER REFERENCES movies ON DELETE CASCADE,
    movies_genres_genre_id INTEGER REFERENCES genres ON DELETE CASCADE,
    PRIMARY KEY (movies_genres_movie_id, movies_genres_genre_id)
);

CREATE UNIQUE INDEX user_unique ON users(LOWER(user_username));
CREATE UNIQUE INDEX movie_unique ON movies(LOWER(movie_name));
CREATE UNIQUE INDEX genre_unique ON genres(LOWER(genre_name));