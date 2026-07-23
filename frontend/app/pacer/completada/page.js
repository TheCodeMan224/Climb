"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api, getUsuario } from "../../../lib/api";
import { t, getLang } from "../../../lib/i18n";

export default function PacerCompletada() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [lang, setLang] = useState("en");
  const [sugerencias, setSugerencias] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const u = getUsuario();
    if (!u) { router.push("/login"); return; }
    setUser(u); setLang(getLang());
    (async () => {
      try {
        const r = await api(`/api/usuarios/${u.id_usuario}/misiones/sugerencias`);
        setSugerencias(r.sugerencias || []);
      } catch (err) { setError(err.message); }
    })();
  }, [router]);

  const tr = (k) => t(k, lang);

  async function elegir(mision) {
    if (busy) return;
    setBusy(true);
    try {
      await api(`/api/usuarios/${user.id_usuario}/misiones`, { method: "POST", body: { mision } });
      router.push("/pacer");
    } catch (err) { setError(err.message); setBusy(false); }
  }

  if (!user) return null;

  return (
    <main>
      <Link className="link" href="/dashboard">{tr("back_dashboard")}</Link>
      <h1 style={{ marginTop: 16 }}>{tr("mission_complete")}</h1>
      <p className="sub">{tr("next_intro")}</p>
      {error && <p className="error">{error}</p>}
      {!sugerencias && !error && <p className="muted">{tr("pacer_thinking")}</p>}
      {sugerencias && sugerencias.map((s, i) => (
        <div className="card" key={i}>
          <strong>{s.nombre_mision}</strong>
          <p className="muted">{s.descripcion}</p>
          <p className="muted">{(s.acciones || []).length} {tr("actions_word")}</p>
          <button className="btn" disabled={busy} onClick={() => elegir(s)}>{busy ? tr("setting_up") : tr("choose")}</button>
        </div>
      ))}
    </main>
  );
}
