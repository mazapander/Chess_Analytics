type Props = {
  label: string;
  value: string | number;
  detail?: string;
  tone?: "neutral" | "positive" | "negative";
};

export function MetricCard({ label, value, detail, tone = "neutral" }: Props) {
  return (
    <article className={`metric-card metric-card--${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
      {detail && <small>{detail}</small>}
    </article>
  );
}
