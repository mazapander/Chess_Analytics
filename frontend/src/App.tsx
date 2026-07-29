import { useEffect, useState } from "react";

type Overview = {
  games: number;
  wins: number;
  draws: number;
  losses: number;
  score_percentage: number | null;
  monthly_trend: Array<{ month: string; games: number; score_percentage: number | null }>;
  top_openings: Array<{ opening: string; games: number; score_percentage: number | null }>;
};

const API_URL = import.meta.env.VITE_ANALYTICS_API_URL ?? "http://localhost:8002";

export default function App() {
  const [data, setData] = useState<Overview | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API_URL}/api/v1/analytics/overview`)
      .then((response) => {
        if (!response.ok) throw new Error("No se pudo cargar el análisis");
        return response.json();
      })
      .then(setData)
      .catch((err: Error) => setError(err.message));
  }, []);

  return (
    <main>
      <header>
        <p className="eyebrow">mazapander0</p>
        <h1>Entiende cómo juegas</h1>
        <p>Primera vista descriptiva de tus partidas importadas desde Chess.com.</p>
      </header>

      {error && <section className="panel">{error}</section>}
      {!data && !error && <section className="panel">Cargando análisis…</section>}

      {data && (
        <>
          <section className="metrics">
            <article><span>Partidas</span><strong>{data.games}</strong></article>
            <article><span>Victorias</span><strong>{data.wins}</strong></article>
            <article><span>Tablas</span><strong>{data.draws}</strong></article>
            <article><span>Derrotas</span><strong>{data.losses}</strong></article>
            <article><span>Puntuación</span><strong>{data.score_percentage ?? "—"}%</strong></article>
          </section>

          <section className="grid">
            <article className="panel">
              <h2>Evolución mensual</h2>
              {data.monthly_trend.map((row) => (
                <div className="row" key={row.month}>
                  <span>{row.month}</span>
                  <span>{row.games} partidas · {row.score_percentage ?? "—"}%</span>
                </div>
              ))}
            </article>
            <article className="panel">
              <h2>Aperturas más frecuentes</h2>
              {data.top_openings.slice(0, 8).map((row) => (
                <div className="row" key={row.opening}>
                  <span>{row.opening}</span>
                  <span>{row.games} · {row.score_percentage ?? "—"}%</span>
                </div>
              ))}
            </article>
          </section>
        </>
      )}
    </main>
  );
}
