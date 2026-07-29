# Fase 1: análisis y comprensión del jugador

## Objetivo

Transformar las partidas importadas de `mazapander0` en información longitudinal que permita entender resultados, hábitos, aperturas, gestión del tiempo y, posteriormente, errores evaluados con motor.

Esta fase no incluye todavía entrenamiento interactivo ni repetición espaciada.

## Arquitectura

### `ingestion-api`

Responsable exclusivamente de:

- consultar Chess.com;
- importar el histórico o un mes concreto;
- normalizar PGN y movimientos;
- registrar ejecuciones de importación.

Puerto local: `8001`.

### `analytics-api`

Responsable exclusivamente de:

- consultar partidas almacenadas;
- calcular agregados y tendencias;
- exponer datos para visualización;
- incorporar posteriormente resultados de Stockfish.

Puerto local: `8002`.

### `frontend`

Aplicación React + TypeScript + Vite gestionada con pnpm.

Responsable de:

- resumen general;
- tendencias mensuales;
- rendimiento por color y ritmo;
- aperturas más frecuentes;
- navegación futura por partidas y momentos críticos.

Puerto local: `5173`.

### PostgreSQL

Base de datos compartida. Los servicios comparten modelos y migraciones, pero no responsabilidades de API.

## Entrega inicial

El primer endpoint descriptivo es:

`GET /api/v1/analytics/overview`

Acepta filtros opcionales:

- `date_from`;
- `date_to`;
- `time_class`.

Devuelve:

- partidas, victorias, tablas y derrotas;
- porcentaje de puntuación;
- rating medio propio y rival;
- rendimiento por color;
- rendimiento por ritmo;
- evolución mensual;
- aperturas más frecuentes.

## Siguiente bloque de análisis

1. Integrar Stockfish como worker separado.
2. Guardar evaluación antes y después de cada movimiento propio.
3. Calcular pérdida de centipawns y pérdida de probabilidad de resultado.
4. Identificar momentos críticos por partida.
5. Agregar errores por fase, color, apertura, tiempo disponible y periodo.
6. Exponer tendencias y partidas representativas.

## Principio de producto

El sistema debe priorizar patrones repetidos y cambios en el tiempo. Una jugada mala aislada es un incidente; varias decisiones similares con impacto recurrente constituyen una tendencia entrenable.
