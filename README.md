# Book Management API

#### A RESTful API built with FastAPI for managing users, authors, books and genres

## Features
- User registration and authentication with JWT
- Role-based permissions (user, admin)
- Filtering, Pagination and Sorting for retrieve books endpoint
- Import and Export books in JSON and CSV formats
- Unit and Integration tests with database for testing
- Custom Validation and Error Handling
- Rate-limiter for only 5 requests per 1 minute for each endpoint
- Deployed on AWS Lambda and RDS

## Next steps
1. Personalized Book Recommendation System

    To implement this system we need to provide some changes:
    - Create a table like `user_activity(book_id, user_id, action, timestamp)`
    - Log actions such as: viewed, opened details, favorited, exported
    - Prepare recommendation data
        - For collaborative filtering
            - Use `user_id` and `book_id` interactions
        - For content-based filtering
            - Use book `genre`, `author_ids`, `published_year`, etc.
    - Build a simple ML model
        - Use libraries
            - `Surprise` - for collaborative filtering
            - `LightFM` – hybrid (collaborative + content-based)
    - Add `/recommendations/` route

2. Testing

    To make sure API works correctly without making manual testing we need to provide Integration and Unit tests.
    | Module | Unit tests | Integration tests |
    | ------ | ---------- | ----------------- |
    | Auth | + | + |
    | Author | - | - |
    | Books | - | - |
    | Genre | - | - |
    | Admin | - | - |

## Tech Stack
- Python 3.12
- FastAPI
- PostgreSQL
- `uv` package manager (`pyproject.toml`, `uv.lock`)

## Deploy
This API is deployed on AWS Lambda with FastAPI + Mangum, connected to a PostgreSQL instance on AWS RDS.
- Public endpoint: [url](https://y5h7vnrm7elq6fw2skg3eic7fm0rtfva.lambda-url.eu-north-1.on.aws/)

>**Note:** Currently some endpoints do not work, i had no experience with Lambda so i do not know why, trying to fix

## Build & Run Locally
1. Setup .env file (in general directory ./.env)
    - TESTING=0
    - DB_USER
    - DB_PASSWORD
    - DB_HOST
    - DB_PORT
    - DB_NAME
    - DB_USER_TEST
    - DB_PASSWORD_TEST
    - DB_HOST_TEST
    - DB_PORT_TEST
    - DB_NAME_TEST
    - JWT_SECRET_KEY
    - JWT_ALGORITHM
    - JWT_ACCESS_TOKEN_EXPIRE_MINUTES

2. Setup `uv`
    - Install it to global python interpreter ([docs](https://docs.astral.sh/uv/))
    - `uv pip install -r pyproject.toml`

3. Make a migrations
    - `psql -h <host> -U <user> -d <dbname> -f app\models\schema.sql`

4. Run FastAPI
    - `uv run uvicorn app.main:app --reload`

5. Add admin user (optional)
    - Create user follow the endpoints
    - `psql -h <host> -U <user> -d <dbname>`
    - `UPDATE users SET is_admin = TRUE WHERE id = <created_user_id>;`

6. Run tests (optional)
    - `uv run pytest -v`

## API Endpoints
Also you can find API Documentation following endpoints
- Swagger UI: `/docs`
- ReDoc: `/redoc`

### Auth

| Method | Endpoint         | Description                | Payload                         |
| ------ | ---------------- | -------------------------- | ------------------------------- |
| POST   | `/auth/register` | Register a new user        | username: str, password_1: str, password_2: str |
| POST   | `/auth/login`    | Get JWT access token       | username: str, password: str    |
| GET    | `/auth/me`       | Get current logged-in user | -                               |

---

### Admin (Admin-only access)

| Method | Endpoint             | Description                  | Payload                                                                                                |
| ------ | -------------------- | ---------------------------- | ------------------------------------------------------------------------------------------------------ |
| POST   | `/admin/author`      | Create author linked to user | name: str, user_id: int                                                                               |
| PUT    | `/admin/author/{id}` | Update author by ID          | name: str, user_id: int                                                                               |
| DELETE | `/admin/author/{id}` | Delete author by ID          | -                                                                                                      |
| POST   | `/admin/genre`       | Create new genre             | name: str                                                                                              |
| PUT    | `/admin/genre/{id}`  | Update genre by ID           | name: str                                                                                              |
| DELETE | `/admin/genre/{id}`  | Delete genre by ID           | -                                                                                                      |
| POST   | `/admin/books`       | Create a new book            | title: str, genre_id: int, published_year: int, author_ids: list\[int], created_by: Optional\[int] |
| PUT    | `/admin/books/{id}`  | Update book by ID            | title: str, genre_id: int, published_year: int, author_ids: list\[int], created_by: Optional\[int] |
| DELETE | `/admin/books/{id}`  | Delete book by ID            | -                                                                                                      |

---

### Author

| Method | Endpoint         | Description                | Payload   |
| ------ | ---------------- | -------------------------- | --------- |
| POST   | `/author/create` | Create author (1 per user) | name: str |
| GET    | `/author/{id}`   | Get author by ID           | -         |
| PATCH  | `/author/{id}`   | Update author by ID        | name: str |

---

### Books

| Method | Endpoint        | Description                      | Payload                                                                   |
| ------ | --------------- | -------------------------------- | ------------------------------------------------------------------------- |
| POST   | `/books/create` | Create book (by linked author)   | title: str, genre\_id: int, published\_year: int, author\_ids: list\[int] |
| GET    | `/books/`       | List books (with filters/export) | query params                                                              |
| GET    | `/books/{id}`   | Get book by ID                   | -                                                                         |
| PUT    | `/books/{id}`   | Update book (only by creator)    | title: str, genre\_id: int, published\_year: int, author\_ids: list\[int]                                                            |
| DELETE | `/books/{id}`   | Delete book (only by creator)    | -                                                                         |
| POST   | `/books/import` | Import books from CSV/JSON file  | file: UploadFile                                                          |

---

### Genre

| Method | Endpoint      | Description     | Payload |
| ------ | ------------- | --------------- | ------- |
| GET    | `/genre/`     | List all genres | -       |
| GET    | `/genre/{id}` | Get genre by ID | -       |

---

## Book Filtering & Export (GET `/books/`)

| Query Param   | Example                 | Description                      |
| ------------- | ----------------------- | -------------------------------- |
| `page`        | `?page=2`               | Pagination page                  |
| `limit`       | `?limit=20`             | Items per page                   |
| `sort_by`     | `?sort_by=title`        | Sort field (`id`, `title`, etc.) |
| `sort_order`  | `?sort_order=desc`      | `asc` or `desc`                  |
| `title`       | `?title=harry`          | Filter by book title             |
| `author_name` | `?author_name=rowling`  | Filter by author name            |
| `genre_id`    | `?genre_id=3`           | Filter by genre ID               |
| `year_from`   | `?year_from=2000`       | Filter by publish year from      |
| `year_to`     | `?year_to=2020`         | Filter by publish year to        |
| `export`      | `?export=json` or `csv` | Export books as JSON or CSV      |

---

## Author
Developed by Borodianskyi Mykhailo.