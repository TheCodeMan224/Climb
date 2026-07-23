"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, getUsuario } from "../../lib/api";
import { t, getLang } from "../../lib/i18n";

export default function Caminos() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [lang, setLang] = useState("en");
  const [caminos, setCaminos] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    const u = getUsuario();
    if (!u) { router.push("/login"); return; }
    setUser(u); setLang(getLang());
    let diagnostico = null;
    try { diagnostico = JSON.parse(localStorage.getItem("climb_diagnostico")); } catch { diagnostico = null; }
    (async () => {
      try {
        const r = await api(`/api/usuarios/${u.id_usuario}/caminos`, { method: "POST", body: { diagnostico } });
        setCaminos(r.caminos || []);
      } catch (err) { setError(err.message); }
    })();
  }, [router]);

  const tr = (k) => t(k, lang);

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
      await api(`/api/usuarios/${user.id_usuario}/mision`, { method: "POST" });
      router.push("/dashboard");
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  }

  if (!user) return null;
  if (error) return <main><p className="error">{error}</p></main>;
  if (!caminos) return <main><p className="muted">{tr("preparing_paths")}</p></main>;

  return (
    <main>
      <h1>{tr("caminos_title")}</h1>
      <p className="sub">{tr("caminos_sub")}</p>
      {caminos.map((c, i) => (
        <div className="card" key={i}>
          <strong style={{ fontSize: 18 }}>{c.nombre}</strong>
          <p>{c.descripcion}</p>
          {c.por_que_encaja && (<p className="muted"><em>{tr("why_fits")}</em> {c.por_que_encaja}</p>)}
          <p className="muted"><strong>{tr("tradeoff")}:</strong> {c.tradeoff_principal} &nbsp;·&nbsp; <strong>{tr("risk")}:</strong> {c.riesgo_principal}</p>
          <p className="muted"><strong>{tr("time_week")}:</strong> {c.tiempo_estimado_semanal} &nbsp;·&nbsp; <strong>{tr("pattern_breaks")}:</strong> {c.patron_que_rompe}</p>
          <button className="btn" disabled={busy} onClick={() => elegir(c)}>
            {busy ? tr("preparing_mission") : tr("take_path")}
          </button>
        </div>
      ))}
    </main>
  );
}
