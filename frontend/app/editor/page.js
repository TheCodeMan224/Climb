"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api, getUsuario } from "../../lib/api";
import { t, getLang } from "../../lib/i18n";
import Wordmark from "../components/Wordmark";
import AgentMark from "../components/AgentMark";

export default function EditorHome() {
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
      try { setData(await api(`/api/usuarios/${u.id_usuario}/editor/borradores`)); }
      catch (err) { setError(err.message); }
    })();
  }, [router]);

  const tr = (k) => t(k, lang);
  if (!user) return null;

  const Lista = ({ titulo, items }) =>
    items.length > 0 && (
      <>
        <h2>{titulo}</h2>
        {items.map((b) => (
          <Link key={b.id} href={`/editor/estudio?id=${b.id}`} className="card" style={{ display: "block", textDecoration: "none", color: "inherit" }}>
            <strong>{b.es_correo && b.asunto ? b.asunto : b.formato || "Draft"}</strong>
            <p className="muted" style={{ margin: "6px 0 0" }}>{b.preview} · {b.hace}</p>
          </Link>
        ))}
      </>
    );

  return (
    <main>
      <div className="topbar"><Wordmark href="/dashboard" /></div>
      <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 10 }}>
        <AgentMark name="Editor" size={44} />
        <h1 style={{ margin: 0 }}>{tr("editor")}</h1>
      </div>
      <p className="sub">{tr("editor_intro")}</p>
      <button className="btn" onClick={() => router.push("/editor/estudio")}>{tr("new_draft")}</button>
      {error && <p className="error">{error}</p>}
      {data && (
        <>
          <Lista titulo={tr("active_drafts")} items={data.activos} />
          <Lista titulo={tr("completed")} items={data.completados} />
          {data.activos.length === 0 && data.completados.length === 0 && (
            <p className="muted" style={{ marginTop: 20 }}>{tr("no_drafts")}</p>
          )}
        </>
      )}
    </main>
  );
}
