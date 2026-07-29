# Chess Analytics

Backend personal para descargar las partidas públicas de `mazapander0` desde Chess.com, almacenar el PGN y normalizar todos los movimientos en PostgreSQL.

## Stack

- FastAPI
- PostgreSQL
- SQLAlchemy 2
- Alembic
- python-chess
- HTTPX
- Docker Compose

## Arranque rápido

```bash
cp .env.example .env
docker compose up --build
```

La API quedará disponible en `http://localhost:8000` y la documentación en `http://localhost:8000/docs`.

Ejecuta la migración inicial:

```bash
docker compose exec api alembic upgrade head
```

Importa todo el histórico disponible:

```bash
curl -X POST http://localhost:8000/api/v1/imports/all
```

Importa solo un mes:

```bash
curl -X POST http://localhost:8000/api/v1/imports/2026/7
```

## Endpoints iniciales

- `GET /health`
- `GET /api/v1/games`
- `GET /api/v1/games/{game_id}`
- `GET /api/v1/games/{game_id}/moves`
- `POST /api/v1/imports/all`
- `POST /api/v1/imports/{year}/{month}`

## Modelo de datos

### `games`

Guarda metadatos de Chess.com, jugadores, ratings, resultado, control de tiempo, PGN completo, URL y estado futuro de análisis.

### `moves`

Guarda cada media jugada con SAN, UCI, FEN anterior/posterior, pieza, casillas, banderas tácticas básicas y reloj cuando el PGN lo incluye.

### `import_runs`

Registra cada sincronización, su estado, rango consultado, partidas encontradas, creadas, actualizadas y errores.

## Desarrollo local sin Docker

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
alembic upgrade head
uvicorn app.main:app --reload
```

## Decisiones de diseño

- El username se configura con `CHESS_USERNAME` y por defecto es `mazapander0`.
- El PGN bruto se conserva como fuente original.
- Las partidas se deduplican por URL de Chess.com.
- Los movimientos se regeneran cuando una partida existente cambia.
- La importación consulta los archivos mensuales de forma secuencial para respetar la PubAPI de Chess.com.
- El esquema deja preparado `analysis_status` para incorporar Stockfish en una fase posterior.
