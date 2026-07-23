"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api, getUsuario, clearUsuario } from "../../lib/api";
import { t, getLang } from "../../lib/i18n";

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

  return (
    <main>
      <div className="row" style={{ justifyContent: "space-between" }}>
        <h1 style={{ margin: 0 }}>{tr("hi")}, {user.nombre}</h1>
        <button className="link" onClick={logout} style={{ background: "none", border: "none", cursor: "pointer" }}>{tr("sign_out")}</button>
      </div>
      <p className="muted">{user.handle} · {user.idioma?.toUpperCase()}</p>

      {resumen?.voice_profile?.tono_natural && (<p className="pivote" style={{ marginTop: 8 }}>{resumen.voice_profile.tono_natural}</p>)}

      {(resumen?.patrones_consolidados || []).length > 0 && (
        <>
          <h2>{tr("scout_patterns")}</h2>
          {resumen.patrones_consolidados.slice(0, 2).map((p, i) => (
            <div className="card" key={i}><strong>{p.nombre}</strong><p className="muted" style={{ margin: "6px 0 0" }}>{p.descripcion}</p></div>
          ))}
        </>
      )}

      {camino?.nombre_camino && (
        <>
          <h2>{tr("your_path")}</h2>
          <div className="card" style={{ background: "var(--navy)", color: "var(--offwhite)" }}>
            <strong>{camino.nombre_camino}</strong>
            <p style={{ margin: "6px 0 0" }}>{camino.descripcion_camino}</p>
          </div>
        </>
      )}

      <h2>{tr("active_mission")}</h2>
      {mision ? (
        <div className="card">
          <strong>{mision.mision?.nombre_mision}</strong>
          <p className="muted">{mision.mision?.descripcion}</p>
          <Link className="link" href="/pacer">→</Link>
        </div>
      ) : (
        <p className="muted">{tr("no_mission")}</p>
      )}

      <h2>{tr("your_agents")}</h2>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
        {AGENTES.map(([nombre, ruta, desc]) => (
          <Link key={ruta} href={ruta} className="card" style={{ textDecoration: "none", color: "inherit" }}>
            <strong style={{ color: "var(--amber)" }}>{nombre}</strong>
            <p className="muted" style={{ margin: "6px 0 0" }}>{desc}</p>
          </Link>
        ))}
      </div>

      <h2>{tr("from_archive")}</h2>
      {logros.length ? (
        logros.map((l) => (
          <div className="card" key={l.id}><strong>{l.titulo}</strong><p className="muted">{l.tipo} · {l.fecha_corta}</p></div>
        ))
      ) : (
        <p className="muted">{tr("no_wins")}</p>
      )}
    </main>
  );
}
