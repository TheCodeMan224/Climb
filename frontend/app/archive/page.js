"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api, getUsuario } from "../../lib/api";

export default function Archive() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [data, setData] = useState(null); // {stats, meses}
  const [error, setError] = useState("");

  useEffect(() => {
    const u = getUsuario();
    if (!u) {
      router.push("/login");
      return;
    }
    setUser(u);
    (async () => {
      try {
        setData(await api(`/api/usuarios/${u.id_usuario}/archive/timeline`));
      } catch (err) {
        setError(err.message);
      }
    })();
  }, [router]);

  function verFicha(logro) {
    localStorage.setItem("climb_ficha", JSON.stringify({ ...logro, _guardado: true }));
    router.push("/archive/ficha");
  }

  if (!user) return null;

  return (
    <main>
      <Link className="link" href="/dashboard">← Back to dashboard</Link>
      <h1 style={{ marginTop: 16 }}>The Archive</h1>
      <p className="sub">Everything you documented, for when you need it.</p>
      <button className="btn" onClick={() => router.push("/archive/chat")}>+ Document a win</button>

      {error && <p className="error">{error}</p>}
      {data && (
        <>
          <p className="muted" style={{ marginTop: 24 }}>
            {data.stats.total} wins · {data.stats.este_trimestre} this quarter · {data.stats.impacto} impact
          </p>
          {Object.keys(data.meses).length === 0 && (
            <p className="muted">You haven&apos;t documented any wins yet.</p>
          )}
          {Object.entries(data.meses).map(([mes, logros]) => (
            <div key={mes}>
              <h2>{mes}</h2>
              {logros.map((l) => (
                <div className="card" key={l.id} onClick={() => verFicha(l)} style={{ cursor: "pointer" }}>
                  <strong>{l.titulo}</strong>
                  <p className="muted">{l.tipo} · {l.fecha_corta}{l.metric_destacada ? ` · ${l.metric_destacada.value}` : ""}</p>
                </div>
              ))}
            </div>
          ))}
        </>
      )}
    </main>
  );
}
