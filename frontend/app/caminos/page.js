"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, getUsuario } from "../../lib/api";

export default function Caminos() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [caminos, setCaminos] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    const u = getUsuario();
    if (!u) {
      router.push("/login");
      return;
    }
    setUser(u);
    let diagnostico = null;
    try {
      diagnostico = JSON.parse(localStorage.getItem("climb_diagnostico"));
    } catch {
      diagnostico = null;
    }
    (async () => {
      try {
        // Si tenemos el diagnóstico lo pasamos; si no, el backend lo regenera.
        const r = await api(`/api/usuarios/${u.id_usuario}/caminos`, {
          method: "POST",
          body: { diagnostico },
        });
        setCaminos(r.caminos || []);
      } catch (err) {
        setError(err.message);
      }
    })();
  }, [router]);

  async function elegir(camino) {
    if (busy) return;
    setBusy(true);
    setError("");
    try {
      const alternativos = caminos.filter((c) => c !== camino);
      await api(`/api/usuarios/${user.id_usuario}/camino-elegido`, {
        method: "POST",
        body: {
          nombre_camino: camino.nombre || "",
          descripcion_camino: camino.descripcion || "",
          tradeoff_principal: camino.tradeoff_principal || "",
          riesgo_principal: camino.riesgo_principal || "",
          tiempo_estimado_semanal: camino.tiempo_estimado_semanal || "",
          patron_que_rompe: camino.patron_que_rompe || "",
          caminos_alternativos: alternativos,
        },
      });
      // Pacer genera la primera misión antes de ir al dashboard.
      await api(`/api/usuarios/${user.id_usuario}/mision`, { method: "POST" });
      router.push("/dashboard");
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  }

  if (!user) return null;
  if (error) return <main><p className="error">{error}</p></main>;
  if (!caminos) return <main><p className="muted">Preparing your three paths…</p></main>;

  return (
    <main>
      <h1>Your plan for the next 30 days</h1>
      <p className="sub">Three possible paths. You decide which to take.</p>
      {caminos.map((c, i) => (
        <div className="card" key={i}>
          <strong style={{ fontSize: 18 }}>{c.nombre}</strong>
          <p>{c.descripcion}</p>
          {c.por_que_encaja && (
            <p className="muted"><em>Why it fits you:</em> {c.por_que_encaja}</p>
          )}
          <p className="muted">
            <strong>Tradeoff:</strong> {c.tradeoff_principal} &nbsp;·&nbsp;
            <strong>Risk:</strong> {c.riesgo_principal}
          </p>
          <p className="muted">
            <strong>Time/week:</strong> {c.tiempo_estimado_semanal} &nbsp;·&nbsp;
            <strong>Pattern it breaks:</strong> {c.patron_que_rompe}
          </p>
          <button className="btn" disabled={busy} onClick={() => elegir(c)}>
            {busy ? "Preparing your mission…" : "Take this path"}
          </button>
        </div>
      ))}
    </main>
  );
}
