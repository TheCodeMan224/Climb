"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, getUsuario, clearUsuario } from "../../lib/api";

export default function Dashboard() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [mision, setMision] = useState(null);
  const [logros, setLogros] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const u = getUsuario();
    if (!u) {
      router.push("/login");
      return;
    }
    (async () => {
      try {
        const info = await api(`/api/usuarios/${u.id_usuario}`);
        setUser(info);
        // Misión activa (puede no existir -> 404, lo tratamos como "sin misión").
        try {
          setMision(await api(`/api/usuarios/${u.id_usuario}/mision`));
        } catch {
          setMision(null);
        }
        setLogros(await api(`/api/usuarios/${u.id_usuario}/logros`));
      } catch (err) {
        setError(err.message);
      }
    })();
  }, [router]);

  function logout() {
    clearUsuario();
    router.push("/");
  }

  if (error) return <main><p className="error">{error}</p></main>;
  if (!user) return null;

  return (
    <main>
      <div className="row" style={{ justifyContent: "space-between" }}>
        <h1 style={{ margin: 0 }}>Hi, {user.nombre}</h1>
        <button className="link" onClick={logout} style={{ background: "none", border: "none", cursor: "pointer" }}>
          Sign out
        </button>
      </div>
      <p className="muted">{user.handle} · {user.idioma?.toUpperCase()}</p>

      <h2>Active mission</h2>
      {mision ? (
        <div className="card">
          <strong>{mision.mision?.nombre_mision}</strong>
          <p className="muted">{mision.mision?.descripcion}</p>
          <ul>
            {(mision.mision?.acciones || []).map((a, i) => (
              <li key={i}>{a}</li>
            ))}
          </ul>
        </div>
      ) : (
        <p className="muted">No mission yet.</p>
      )}

      <h2>From the archive</h2>
      {logros.length ? (
        logros.map((l) => (
          <div className="card" key={l.id}>
            <strong>{l.titulo}</strong>
            <p className="muted">{l.tipo} · {l.fecha_corta}</p>
          </div>
        ))
      ) : (
        <p className="muted">No wins documented yet.</p>
      )}
    </main>
  );
}
