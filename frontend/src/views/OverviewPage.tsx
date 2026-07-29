import { DataListPanel } from "../components/dashboard/DataListPanel";
import { MetricCard } from "../components/dashboard/MetricCard";
import { useOverview } from "../hooks/useOverview";

export function OverviewPage() {
  const { data, error, loading } = useOverview();

  if (loading) return <section className="state-panel">Cargando análisis…</section>;
  if (error) return <section className="state-panel state-panel--error">{error}</section>;
  if (!data) return <section className="state-panel">No hay datos disponibles.</section>;

  const monthlyRows = data.monthly_trend.slice(-8).reverse().map((row) => ({
    label: row.month,
    value: `${row.games} partidas · ${row.score_percentage ?? "—"}%`,
  }));
  const openingRows = data.top_openings.slice(0, 8).map((row) => ({
    label: row.opening,
    value: `${row.games} · ${row.score_percentage ?? "—"}%`,
  }));

  return (
    <>
      <header className="page-header" id="overview">
        <div>
          <p className="eyebrow">Panel personal</p>
          <h1>Tu juego, explicado con datos</h1>
          <p className="lead">Resultados, evolución y primeras señales de rendimiento de mazapander0.</p>
        </div>
        <div className="engine-badge"><span className="status-dot" />Stockfish worker activo</div>
      </header>

      <section className="metrics-grid" aria-label="Métricas principales">
        <MetricCard label="Partidas" value={data.games} detail="Histórico analizado" />
        <MetricCard label="Victorias" value={data.wins} detail={`${data.score_percentage ?? "—"}% de puntuación`} tone="positive" />
        <MetricCard label="Tablas" value={data.draws} />
        <MetricCard label="Derrotas" value={data.losses} tone="negative" />
        <MetricCard label="Rating medio" value={data.average_player_rating ?? "—"} detail={`Rivales: ${data.average_opponent_rating ?? "—"}`} />
      </section>

      <section className="content-grid">
        <DataListPanel title="Evolución mensual" subtitle="Actividad y puntuación obtenida" rows={monthlyRows} />
        <DataListPanel title="Aperturas frecuentes" subtitle="Volumen y rendimiento" rows={openingRows} />
      </section>

      <section className="panel insight-panel" id="patterns">
        <div><p className="eyebrow">Siguiente capa</p><h2>Patrones de decisión</h2></div>
        <p>El worker almacena evaluación, mejor movimiento, pérdida de centipawns y clasificación por cada movimiento propio. La siguiente vista agregará errores y momentos críticos.</p>
      </section>
    </>
  );
}
