"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api, getUsuario } from "../../lib/api";
import { t, getLang } from "../../lib/i18n";

export default function ClarityEspejo() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [lang, setLang] = useState("en");
  const [espejo, setEspejo] = useState(null);
  const [texto, setTexto] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    const u = getUsuario();
    if (!u) { router.push("/login"); return; }
    setUser(u); setLang(getLang());
    (async () => {
      try { setEspejo(await api(`/api/usuarios/${u.id_usuario}/clarity/espejo`)); }
      catch (err) { setError(err.message); }
    })();
  }, [router]);

  const tr = (k) => t(k, lang);

  function empezar() {
    const tx = texto.trim();
    if (!tx) return;
    localStorage.setItem("climb_clarity_inicial", tx);
    localStorage.removeItem("climb_clarity_turns");
    router.push("/clarity/conversacion");
  }

  if (!user) return null;

  return (
    <main>
      <Link className="link" href="/dashboard">{tr("back_dashboard")}</Link>
      <h1 style={{ marginTop: 16 }}>{tr("clarity_built")}{espejo?.nombre ? `, ${espejo.nombre}` : ""}</h1>
      {error && <p className="error">{error}</p>}
      {espejo && espejo.bloques.map((b, i) => (
        <div className="card" key={i}>
          <div className="muted" style={{ fontSize: 12, textTransform: "uppercase" }}>{b.numero} · {b.agente}</div>
          <p style={{ margin: "6px 0 0" }}>
            {b.segmentos.map(([tx, esDato], j) => (
              <span key={j} style={esDato ? { color: "var(--amber)", fontWeight: 700 } : undefined}>{tx}</span>
            ))}
          </p>
          {b.cta_texto && b.cta_ruta && <Link className="link" href={b.cta_ruta} style={{ display: "inline-block", marginTop: 8 }}>{b.cta_texto}</Link>}
        </div>
      ))}
      <h2>{tr("now_you")}</h2>
      <p className="sub">{tr("clarity_prompt")}</p>
      <textarea value={texto} onChange={(e) => setTexto(e.target.value)} placeholder={tr("clarity_placeholder")} />
      <button className="btn" onClick={empezar}>{tr("start")}</button>
    </main>
  );
}
