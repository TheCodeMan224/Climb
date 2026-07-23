"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api, getUsuario } from "../../lib/api";
import { t, getLang } from "../../lib/i18n";

export default function Archive() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [lang, setLang] = useState("en");
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const u = getUsuario();
    if (!u) { router.push("/login"); return; }
    setUser(u); setLang(getLang());
    (async () => {
      try { setData(await api(`/api/usuarios/${u.id_usuario}/archive/timeline`)); }
      catch (err) { setError(err.message); }
    })();
  }, [router]);

  const tr = (k) => t(k, lang);

  function verFicha(logro) {
    localStorage.setItem("climb_ficha", JSON.stringify({ ...logro, _guardado: true }));
    router.push("/archive/ficha");
  }

  if (!user) return null;

  return (
    <main>
      <Link className="link" href="/dashboard">{tr("back_dashboard")}</Link>
      <h1 style={{ marginTop: 16 }}>{tr("the_archive")}</h1>
      <p className="sub">{tr("archive_intro")}</p>
      <button className="btn" onClick={() => router.push("/archive/chat")}>{tr("document_win")}</button>
      {error && <p className="error">{error}</p>}
      {data && (
        <>
          <p className="muted" style={{ marginTop: 24 }}>
            {data.stats.total} {tr("wins")} · {data.stats.este_trimestre} {tr("this_quarter")} · {data.stats.impacto} {tr("impact")}
          </p>
          {Object.keys(data.meses).length === 0 && <p className="muted">{tr("no_wins_yet")}</p>}
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
