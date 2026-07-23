"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api, getUsuario } from "../../lib/api";

export default function EditorHome() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [data, setData] = useState(null); // {activos, completados}
  const [error, setError] = useState("");

  useEffect(() => {
    const u = getUsuario();
    if (!u) {
      router.push("/login");
      return;
    }
    setUser(u);
    (async () => {
      try {
        setData(await api(`/api/usuarios/${u.id_usuario}/editor/borradores`));
      } catch (err) {
        setError(err.message);
      }
    })();
  }, [router]);

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
      <Link className="link" href="/dashboard">← Back to dashboard</Link>
      <h1 style={{ marginTop: 16 }}>Editor</h1>
      <p className="sub">Turn your work into content, in your voice.</p>
      <button className="btn" onClick={() => router.push("/editor/estudio")}>＋ New draft</button>
      {error && <p className="error">{error}</p>}
      {data && (
        <>
          <Lista titulo="Active drafts" items={data.activos} />
          <Lista titulo="Completed" items={data.completados} />
          {data.activos.length === 0 && data.completados.length === 0 && (
            <p className="muted" style={{ marginTop: 20 }}>No drafts yet. Create a new one to start.</p>
          )}
        </>
      )}
    </main>
  );
}
