import sqlite3
from fastapi import FastAPI
import requests
from typing import Any
from pydantic import BaseModel
class Update_Movie_class(BaseModel):
    title: str
    year: int
    actors: str


app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/sum")
def sum(x: int = 0, y: int = 10):
    return x+y

@app.get("/subtract")
def subtract(x: int = 0, y: int = 0):
    return x - y

@app.get("/multiply")
def multiply(x: int = 1, y: int = 1):
    return x * y


@app.get("/geocode")
def sum(lat: float, lon: float):
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    return response.json()

@app.get('/movies')
def get_movies():
    db = sqlite3.connect('movies.db')
    cursor = db.cursor()
    cursor.execute("SELECT id, title, year, actors  FROM movies")
    rows = cursor.fetchall()
    db.close()

    output = []
    for row in rows:
        movie = {
            "id": row[0],
            "title": row[1],
            "year": row[2],
            "actors": row[3]
        }
        output.append(movie)
    return output

@app.get('/movies/{movie_id}')
def get_single_movie(movie_id:int):
    db = sqlite3.connect('movies.db')
    cursor = db.cursor()
    cursor.execute("SELECT id, title, year, actors FROM movies WHERE id = ?", (movie_id,))
    row = cursor.fetchone()
    db.close()

    if row is None:
        return {"message": "Movie not found"}
    else:
        movie = {
            "id": row[0],
            "title": row[1],
            "year": row[2],
            "actors": row[3]
        }
    return movie

@app.post("/movies")
def add_movie(params: dict[str, Any]):
    db = sqlite3.connect("movies.db")
    cursor = db.cursor()

    cursor.execute(
        "INSERT INTO movies (title, year, actors) VALUES (?, ?, ?)",
        (params["title"], params["year"], params["actors"])
    )

    db.commit()
    new_id = cursor.lastrowid
    db.close()

    return {"message": "Movie added successfully", "id": new_id}

@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: int):
    db = sqlite3.connect("movies.db")
    cursor = db.cursor()

    cursor.execute("DELETE FROM movies WHERE id = ?", (movie_id,))
    db.commit()
    deleted = cursor.rowcount
    db.close()

    if deleted == 0:
        return {"message": "Movie not found"}

    return {"message": f"Movie {movie_id} deleted successfully"}

@app.delete("/movies")
def delete_all_movies(confirm: str | None = None):
    if confirm != "yes":
        return {
            "warning": "This will delete ALL movies. To confirm, call: /movies?confirm=yes"
        }

    db = sqlite3.connect("movies.db")
    cursor = db.cursor()

    cursor.execute("DELETE FROM movies")
    db.commit()
    deleted = cursor.rowcount
    db.close()

    return {"message": f"All movies deleted successfully ({deleted} removed)"}

@app.put("/movies/{movie_id}")
def update_movie(movie_id: int, params: Update_Movie_class):
    db = sqlite3.connect("movies.db")
    cursor = db.cursor()

    cursor.execute(
        "UPDATE movies SET title = ?, year = ?, actors = ? WHERE id = ?",
        (params["title"], params["year"], params["actors"], movie_id)
    )

    db.commit()
    updated = cursor.rowcount
    db.close()

    if updated == 0:
        return {"message": "Movie not found"}

    return {"message": f"Movie {movie_id} updated successfully"}

