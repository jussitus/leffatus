from flask import abort, flash, redirect, render_template, request, session, url_for
from app import app
import movies as m
import users as u
import reviews as r


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/movies", methods=["GET", "POST"])
def movies():
    if request.method == "GET":
        query = request.args
        count = m.get_movie_count(query)
        genres = m.get_genres()
        try:
            movies = m.get_movies(query)
        except:
            flash("Virheellinen haku!")
            return redirect("/movies")
        query = query.to_dict()
        sort = query.pop("sort", "name")
        page = query.pop("page", "0")
        order = query.pop("order", "asc")
        return render_template(
            "movies.html",
            movies=movies,
            genres=genres,
            query=query,
            sort=sort,
            page=page,
            order=order,
            count=count,
        )

    if request.method == "POST":
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        movie_name = request.form["movie_name"]
        movie_year = request.form["movie_year"]
        movie_runtime = request.form["movie_runtime"]
        if m.add_movie(movie_name, movie_year, movie_runtime):
            flash("Elokuva lisätty!")
            return redirect("/movies")
        flash(
            "Elokuvan lisääminen ei onnistunut. Se on mahdollisesti jo lisätty aiemmin!"
        )
        return redirect("/movies")
    return render_template(
        "error.html", error="VIRHE: Väärä metodi! Tänne ei pitäisi päästä normaalisti."
    )


@app.route("/users")
def users():
    users = u.get_users()
    return render_template("users.html", users=users)


@app.route("/user/<user_id>")
def user(user_id):
    user = u.get_user(user_id)
    reviews = u.get_reviews(user_id)
    return render_template("user.html", user=user, reviews=reviews)


@app.route("/movie/<movie_id>", methods=["GET", "POST"])
def movie(movie_id):
    if request.method == "GET":
        movie = m.get_movie(movie_id)
        genres = m.get_genres_by_movie(movie_id)
        genre_list = m.get_genres()
        reviews = m.get_reviews(movie_id)
        reviewed = any(session.get("id") == review.review_user_id for review in reviews)
        average_score = 0 if len(reviews) == 0 else r.get_average_score(movie_id)
        return render_template(
            "movie.html",
            movie=movie,
            reviews=reviews,
            average_score=average_score,
            reviewed=reviewed,
            genres=genres,
            genre_list=genre_list,
        )
    if request.method == "POST":
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        user_id = session.get("id")
        review_text = request.form["review_text"]
        review_score = request.form["review_score"]
        if r.add_review(user_id, movie_id, review_text, review_score):
            return redirect(url_for("movie", movie_id=movie_id))
        return render_template(
            "error.html",
            error="VIRHE: Arvostelun lisääminen ei onnistunut! Tänne ei pitäisi päästä normaalisti.",
        )
    return render_template(
        "error.html", error="VIRHE: Väärä metodi! Tänne ei pitäisi päästä normaalisti."
    )


@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    if u.login(username, password):
        return redirect("/")
    flash("Väärä tunnus tai salasana!")
    return redirect("/")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if u.signup(username, password, False):
            return redirect("/")
        flash("Tunnuksen luominen ei onnistunut. Kokeile toista nimeä.")
        return redirect("/signup")
    return redirect("/")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/remove_movie", methods=["POST"])
def remove_movie():
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)
    movie_id = request.form["movie_id"]
    if session["is_admin"] and m.remove_movie(movie_id):
        return redirect("/movies")

    return render_template(
        "error.html",
        error="VIRHE: Elokuvan poistaminen ei onnistunut! Tänne ei pitäisi päästä normaalisti.",
    )


@app.route("/remove_user", methods=["POST"])
def remove_user():
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)
    user_id = request.form["user_id"]
    if session["is_admin"] and u.remove_user(user_id):
        return redirect("/users")
    return render_template(
        "error.html",
        error="VIRHE: Käyttäjätunnuksen poistaminen ei onnistunut! Tänne ei pitäisi päästä normaalisti.",
    )


@app.route("/remove_review", methods=["POST"])
def remove_review():
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)
    review_id = request.form["review_id"]
    movie_id = request.form["movie_id"]
    if session["is_admin"] and r.remove_review(review_id):
        return redirect(f"/movie/{movie_id}")
    return render_template(
        "error.html",
        error="VIRHE: Arvostelun poistaminen ei onnistunut! Tänne ei pitäisi päästä normaalisti.",
    )


@app.route("/admin")
def admin():
    if session and session["is_admin"]:
        genres = m.get_genres()
        return render_template("admin.html", genres=genres)
    return render_template("error.html", error="VIRHE: Ei oikeuksia nähdä tätä sivua.")


@app.route("/add_genre", methods=["POST"])
def add_genre():
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)
    genre_name = request.form["genre_name"]
    if session["is_admin"] and m.add_genre(genre_name):
        return redirect("/admin")
    flash("Genren lisääminen ei onnistunut. Se on mahdollisesti jo lisätty aiemmin!")
    return redirect("/admin")


@app.route("/add_movie_to_genre", methods=["POST"])
def add_movie_to_genre():
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)
    genre_id = request.form["genre_id"]
    movie_id = request.form["movie_id"]
    if session["username"] and m.add_movie_to_genre(genre_id, movie_id):
        return redirect(url_for("movie", movie_id=movie_id))
    return render_template(
        "error.html",
        error="VIRHE: Genren lisääminen elokuvaan ei onnistunut! Tänne ei pitäisi päästä normaalisti.",
    )
