type Row = { label: string; value: string };

type Props = {
  title: string;
  subtitle?: string;
  rows: Row[];
};

export function DataListPanel({ title, subtitle, rows }: Props) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <div><h2>{title}</h2>{subtitle && <p>{subtitle}</p>}</div>
      </div>
      <div className="data-list">
        {rows.map((row) => (
          <div className="data-row" key={`${row.label}-${row.value}`}>
            <span>{row.label}</span><strong>{row.value}</strong>
          </div>
        ))}
      </div>
    </section>
  );
}
