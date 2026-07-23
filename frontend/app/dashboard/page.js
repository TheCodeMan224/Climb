"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api, getUsuario, clearUsuario } from "../../lib/api";
import { t, getLang } from "../../lib/i18n";
import Wordmark from "../components/Wordmark";
import AgentMark from "../components/AgentMark";

export default function Dashboard() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [lang, setLang] = useState("en");
  const [mision, setMision] = useState(null);
  const [logros, setLogros] = useState([]);
  const [resumen, setResumen] = useState(null);
  const [camino, setCamino] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const u = getUsuario();
    if (!u) { router.push("/login"); return; }
    setLang(getLang());
    (async () => {
      try {
        const info = await api(`/api/usuarios/${u.id_usuario}`);
        setUser(info);
        try { setMision(await api(`/api/usuarios/${u.id_usuario}/mision`)); } catch { setMision(null); }
        setLogros(await api(`/api/usuarios/${u.id_usuario}/logros`));
        try { setResumen(await api(`/api/usuarios/${u.id_usuario}/resumen`)); } catch { /* */ }
        try { setCamino(await api(`/api/usuarios/${u.id_usuario}/camino`)); } catch { /* */ }
      } catch (err) { setError(err.message); }
    })();
  }, [router]);

  const tr = (k) => t(k, lang);
  const AGENTES = [
    ["Pacer", "/pacer", tr("ag_pacer_d")],
    ["Mirror", "/mirror", tr("ag_mirror_d")],
    ["Archive", "/archive", tr("ag_archive_d")],
    ["Editor", "/editor", tr("ag_editor_d")],
    ["Clarity", "/clarity", tr("ag_clarity_d")],
  ];

  function logout() { clearUsuario(); router.push("/"); }

  if (error) return <main><p className="error">{error}</p></main>;
  if (!user) return null;

  const total = mision ? (mision.mision?.acciones || []).length : 0;
  const hechas = mision ? (mision.progreso || []).filter(Boolean).length : 0;
  const pct = total ? Math.round((hechas / total) * 100) : 0;

  return (
    <main style={{ maxWidth: 960 }}>
      <div className="topbar" style={{ borderBottom: "1px solid var(--border)", paddingBottom: 24 }}>
        <Wordmark href="/dashboard" />
        <div style={{ display: "flex", alignItems: "center", gap: 24 }}>
          <button className="muted" onClick={logout} style={{ background: "none", border: "none", cursor: "pointer", fontWeight: 500, fontFamily: "var(--inter)" }}>{tr("sign_out")}</button>
          <span style={{ width: 38, height: 38, borderRadius: "50%", background: "var(--navy)", color: "var(--offwhite)", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "var(--syne)", fontWeight: 600, fontSize: 15 }}>
            {(user.nombre || "?").charAt(0).toUpperCase()}
          </span>
        </div>
      </div>

      {/* personal header */}
      <div className="eyebrow" style={{ margin: "44px 0 16px" }}>{user.handle} · {user.idioma?.toUpperCase()}</div>
      <h1>{tr("hi")}, {user.nombre}</h1>
      {resumen?.voice_profile?.tono_natural && (
        <div className="pivote-rule" style={{ maxWidth: 640 }}>
          <p className="pivote" style={{ margin: 0 }}>{resumen.voice_profile.tono_natural}</p>
        </div>
      )}

      {/* active mission — navy card */}
      <h2>{tr("active_mission")}</h2>
      {mision ? (
        <div style={{ background: "var(--navy)", color: "var(--offwhite)", borderRadius: 10, padding: "clamp(28px,4vw,44px)", display: "flex", justifyContent: "space-between", gap: 32, alignItems: "center", flexWrap: "wrap" }}>
          <div style={{ flex: "1 1 300px" }}>
            <h3 style={{ fontFamily: "var(--syne)", fontWeight: 700, fontSize: "clamp(22px,3vw,30px)", margin: "0 0 20px", color: "var(--offwhite)", lineHeight: 1.15 }}>{mision.mision?.nombre_mision}</h3>
            <div style={{ display: "flex", alignItems: "center", gap: 18, maxWidth: 420 }}>
              <div style={{ flex: 1, height: 3, background: "rgba(255,255,255,0.18)", borderRadius: 2 }}>
                <div style={{ height: 3, width: `${pct}%`, background: "var(--gold)", borderRadius: 2 }} />
              </div>
              <span style={{ fontSize: 13, color: "#9FB0C4", whiteSpace: "nowrap" }}>{hechas} {tr("actions_of")} {total} {tr("actions_word")}</span>
            </div>
          </div>
          <Link href="/pacer" className="btn" style={{ marginTop: 0, background: "var(--gold)", color: "var(--navy)" }}>{tr("complete_mission")}</Link>
        </div>
      ) : (
        <p className="muted">{tr("no_mission")}</p>
      )}

      {(resumen?.patrones_consolidados || []).length > 0 && (
        <>
          <h2>{tr("scout_patterns")}</h2>
          {resumen.patrones_consolidados.slice(0, 2).map((p, i) => (
            <div className="card" key={i}><strong>{p.nombre}</strong><p className="muted" style={{ margin: "8px 0 0" }}>{p.descripcion}</p></div>
          ))}
        </>
      )}

      {camino?.nombre_camino && (
        <>
          <h2>{tr("your_path")}</h2>
          <div className="card" style={{ borderTop: "3px solid var(--gold)", borderRadius: "0 0 8px 8px" }}>
            <strong>{camino.nombre_camino}</strong>
            <p style={{ margin: "8px 0 0" }}>{camino.descripcion_camino}</p>
          </div>
        </>
      )}

      {/* agents */}
      <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", margin: "48px 0 0" }}>
        <h2 style={{ margin: 0 }}>{tr("your_agents")}</h2>
      </div>
      <div className="hairline" style={{ margin: "14px 0 0" }} />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(240px, 1fr))", borderLeft: "1px solid var(--border)" }}>
        {AGENTES.map(([nombre, ruta, desc]) => (
          <Link key={ruta} href={ruta} style={{ borderRight: "1px solid var(--border)", borderBottom: "1px solid var(--border)", padding: "28px 26px", textDecoration: "none", color: "inherit", background: "var(--offwhite)" }}>
            <div style={{ marginBottom: 18 }}><AgentMark name={nombre} /></div>
            <div style={{ fontFamily: "var(--syne)", fontWeight: 700, fontSize: 22, marginBottom: 6 }}>{nombre}</div>
            <p className="muted" style={{ margin: 0, lineHeight: 1.5 }}>{desc}</p>
          </Link>
        ))}
      </div>

      {/* from the archive */}
      <h2>{tr("from_archive")}</h2>
      {logros.length ? (
        logros.map((l) => (
          <div className="card" key={l.id}><strong>{l.titulo}</strong><p className="muted" style={{ margin: "6px 0 0" }}>{l.tipo} · {l.fecha_corta}</p></div>
        ))
      ) : (
        <p className="muted">{tr("no_wins")}</p>
      )}
    </main>
  );
}
