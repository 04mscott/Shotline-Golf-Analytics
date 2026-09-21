# Shotline

## Golf Data Analytics Application

This is a personal project I'm building for personal use to track my golf scores, equipment, and specifically, strokes gained and areas/clubs to prioritize.

### Primary Goals

- Implement a user friendly UI for tracking data at the individual shot level in order to allow real-time tracking during play, without slowing pace of play on the course
- Implement detailed analytics centered around strokes gained using the baseline expected stroke values found [here](https://pinflag.io/tools/expected-strokes-table), able to group by shot type, or even by specific club used
- Track equipment down to minute details, from brand (Titleist, TaylorMade, etc.) to model (GTS2, Qi4D, etc.), even down to the shaft brand, flex, loft and lie angles, etc.
- Implement an LLM chatbot to act as a digital caddie, walking the user through areas of their game that needs work and how to work on it, as well as working through equipment concerns/upgrades, and talking about how a round went or is going

### Current Progress

The PostgreSQL database is set up and running in Docker. The schema is managed with Alembic, and the SQLAlchemy models live in `src/golf/db/models.py`. The strokes gained calculation logic still lives in a Jupyter notebook and hasn't been moved into the package yet.

#### Design Decisions

- **Postgres** holds only user-entered data: rounds, strokes, equipment, and handicap history. Course data is also loaded into Postgres, from static JSON files in `data/courses/`.
- **Expected-strokes baselines** are static CSVs in `data/baselines/`, loaded into pandas dicts. They never go in the database.
- **Handicap index** is an in-app estimate calculated from the rounds in the database. There's no GHIN integration, since there's no official API and I don't want to depend on an unofficial one.
- **Analytics code** (`src/golf/analytics/`) takes DataFrames and dicts and never imports from `db/`, so it can be unit tested without a database.

#### Next Steps

- Write `scripts/load_courses.py` to upsert the course JSON into Postgres
- Move the strokes gained logic from the notebook into `src/golf/analytics/`, with tests
- Implement the handicap estimate (score differentials, net double bogey caps, best 8 of last 20)
- Implement an initial UI to begin integrating the backend logic with the user-facing front end
- Implement advanced analytics features to display strokes gained data, focused around easy to understand visualizations using golf themed graphics, as well as a priority ranking of areas of the user's golf game to work on first
- Add a Dockerfile and an `app` service to `docker-compose.yml`, then deploy in order to use on the course

### Getting Started

#### Prerequisites

- Docker Desktop
- Python 3.11+

#### First-time setup

```bash
cp .env.example .env    # set DB_PASSWORD, and use the same password inside DATABASE_URL
docker compose up -d
docker compose ps       # wait for "healthy"

conda deactivate        # if conda's base env is active
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"

alembic upgrade head
```

Check that it worked:

```bash
docker compose exec db psql -U golf -d golf -c '\dt'   # 13 tables + alembic_version
```

#### Day to day

```bash
docker compose up -d          # start the database
source .venv/bin/activate
docker compose stop           # stop it (data is kept)
```

`docker compose down` also keeps the data. Only `docker compose down -v` deletes it. To reset the database from scratch:

```bash
docker compose down -v && docker compose up -d && alembic upgrade head
```

#### Changing the schema

`src/golf/db/models.py` is the source of truth.

1. Edit `models.py`
2. `alembic revision --autogenerate -m "what changed"`
3. Read the generated file in `migrations/versions/` before applying it
4. `alembic upgrade head`
5. `alembic check` should report no new upgrade operations

Things to remember:

- **Don't re-run `sqlacodegen`.** It was a one-time bootstrap, and re-running it would overwrite `models.py`.
- **Views are not managed by autogenerate.** `hole_scores` and `round_scores` are created by the first migration's raw SQL (`migrations/sql/0001_initial_schema.sql`). Any view change needs a hand-written migration using `op.execute(...)`. `include_object` in `migrations/env.py` keeps Alembic from treating them as tables.
- **The first migration runs the SQL file.** Don't edit the SQL file after it's applied. Make changes through new migrations instead.
