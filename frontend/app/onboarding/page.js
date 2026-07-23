"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, getUsuario } from "../../lib/api";
import { t, getLang } from "../../lib/i18n";

export default function Onboarding() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [lang, setLang] = useState("en");
  const [paso, setPaso] = useState(0);
  const [resp, setResp] = useState(Array(9).fill(""));
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const u = getUsuario();
    if (!u) router.push("/login");
    else { setUser(u); setLang(getLang()); }
  }, [router]);

  const tr = (k) => t(k, lang);
  const PREGUNTAS = tr("onb_preguntas");

  function set(i, v) {
    const r = resp.slice();
    r[i] = v;
    setResp(r);
  }

  async function finalizar() {
    setBusy(true);
    setError("");
    try {
      const [a1, a2, a3, a4, a5, a6, a7, a8, a9] = resp;
      await api(`/api/usuarios/${user.id_usuario}/perfil`, {
        method: "POST",
        body: {
          apertura_emocional: `${a1} || ${a2}`,
          contexto_profesional: `${a3} || ${a4}`,
          logro_principal: a5,
          reaccion_presion_visibilidad: a6,
          intentos_previos: a7,
          vision_futuro: a8,
          desahogo_libre: a9,
        },
      });
      const d = await api(`/api/usuarios/${user.id_usuario}/diagnostico`, { method: "POST" });
      localStorage.setItem("climb_diagnostico", JSON.stringify(d));
      router.push("/diagnostico");
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  }

  if (!user) return null;

  const p = PREGUNTAS[paso];
  const ultima = paso === PREGUNTAS.length - 1;

  return (
    <main>
      <p className="muted" style={{ textTransform: "uppercase", fontSize: 12 }}>
        {tr("onb_progress")} {String(paso + 1).padStart(2, "0")} / {PREGUNTAS.length}
      </p>
      <h2 style={{ marginTop: 4 }}>{p.acto}</h2>
      <p className="pivote" style={{ marginTop: 8 }}>{p.q}</p>
      <textarea value={resp[paso]} onChange={(e) => set(paso, e.target.value)}
                placeholder={tr("onb_placeholder")} style={{ minHeight: 120 }} />
      {error && <p className="error">{error}</p>}
      <div className="row">
        {paso > 0 && <button className="link" onClick={() => setPaso(paso - 1)}>{tr("previous")}</button>}
        {!ultima ? (
          <button className="btn" style={{ marginTop: 0 }} onClick={() => setPaso(paso + 1)}>{tr("next")}</button>
        ) : (
          <button className="btn" style={{ marginTop: 0 }} disabled={busy} onClick={finalizar}>
            {busy ? tr("generating_diag") : tr("reach_summit")}
          </button>
        )}
      </div>
    </main>
  );
}
