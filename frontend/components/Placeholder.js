import Link from "next/link";

// Cáscara de una pantalla aún en migración desde Flet. Se irá reemplazando por
// la interacción real de cada agente, rebanada por rebanada.
export default function Placeholder({ title, subtitle }) {
  return (
    <main>
      <Link className="link" href="/dashboard">← Back to dashboard</Link>
      <h1 style={{ marginTop: 16 }}>{title}</h1>
      <p className="sub">{subtitle}</p>
      <div className="card">
        <p className="muted">
          This screen is being migrated from the original app. Its full
          interactions are coming next.
        </p>
      </div>
    </main>
  );
}
