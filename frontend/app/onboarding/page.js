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

  const pct = Math.round(((paso + 1) / PREGUNTAS.length) * 100);

  return (
    <main style={{ maxWidth: 760 }}>
      <div className="eyebrow" style={{ marginBottom: 28 }}>{p.acto}</div>

      <div style={{ display: "flex", gap: "clamp(16px,3vw,32px)", alignItems: "flex-start", marginBottom: 28 }}>
        <div style={{ fontFamily: "var(--syne)", fontWeight: 700, fontSize: "clamp(48px,10vw,80px)", lineHeight: 0.85, letterSpacing: "-0.03em", color: "var(--gold)", flexShrink: 0 }}>
          {String(paso + 1).padStart(2, "0")}
        </div>
        <h1 style={{ fontWeight: 600, fontSize: "clamp(26px,4.4vw,38px)", lineHeight: 1.22, margin: 0, paddingTop: 4 }}>{p.q}</h1>
      </div>

      <textarea value={resp[paso]} onChange={(e) => set(paso, e.target.value)}
                placeholder={tr("onb_placeholder")} style={{ minHeight: 200 }} />
      {error && <p className="error">{error}</p>}

      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginTop: 24 }}>
        <button className="link" onClick={() => setPaso(paso - 1)} disabled={paso === 0}
                style={{ background: "none", border: "none", cursor: paso === 0 ? "default" : "pointer", borderBottom: "none", visibility: paso === 0 ? "hidden" : "visible" }}>
          {tr("previous")}
        </button>
        {!ultima ? (
          <button className="btn" style={{ marginTop: 0 }} onClick={() => setPaso(paso + 1)}>{tr("next")}</button>
        ) : (
          <button className="btn" style={{ marginTop: 0 }} disabled={busy} onClick={finalizar}>
            {busy ? tr("generating_diag") : tr("reach_summit")}
          </button>
        )}
      </div>

      <div style={{ borderTop: "1px solid var(--border)", marginTop: 28, paddingTop: 22 }}>
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 12 }}>
          <span className="muted" style={{ fontWeight: 600, letterSpacing: "0.16em", textTransform: "uppercase", fontSize: 12 }}>
            {tr("onb_progress")} {String(paso + 1).padStart(2, "0")} / {PREGUNTAS.length}
          </span>
        </div>
        <div style={{ height: 2, background: "var(--border)", borderRadius: 1 }}>
          <div style={{ height: 2, width: `${pct}%`, background: "var(--gold)", borderRadius: 1, transition: "width .3s ease" }} />
        </div>
      </div>
    </main>
  );
}
