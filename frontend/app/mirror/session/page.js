"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api, getUsuario } from "../../../lib/api";

export default function MirrorSession() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [patron, setPatron] = useState(null);
  const [turns, setTurns] = useState([]);
  const [pregunta, setPregunta] = useState("");
  const [respuesta, setRespuesta] = useState("");
  const [boundary, setBoundary] = useState(false);
  const [listo, setListo] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const u = getUsuario();
    if (!u) {
      router.push("/login");
      return;
    }
    setUser(u);
    let p = null;
    try {
      p = JSON.parse(localStorage.getItem("climb_mirror_patron"));
    } catch {
      p = null;
    }
    if (!p) {
      router.push("/mirror");
      return;
    }
    setPatron(p);
    const iniciales = p.sesion?.turns || [];
    setTurns(iniciales);
    fetchPregunta(u, p.quote, iniciales, false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [router]);

  async function fetchPregunta(u, quote, t, reanclar) {
    setBusy(true);
    try {
      const r = await api(`/api/usuarios/${u.id_usuario}/mirror/pregunta`, { method: "POST", body: { quote, turns: t, reanclar } });
      setPregunta(r.pregunta);
      setListo(r.listo);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function responder() {
    const ans = respuesta.trim();
    if (!ans || busy) return;
    const nuevos = [...turns, ["mirror", pregunta], ["user", ans]];
    setTurns(nuevos);
    setRespuesta("");
    setBusy(true);
    setError("");
    try {
      const b = await api(`/api/usuarios/${user.id_usuario}/mirror/boundary`, { method: "POST", body: { texto: ans } });
      if (b.boundary) {
        setBoundary(true);
        setBusy(false);
        return;
      }
      await fetchPregunta(user, patron.quote, nuevos, false);
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  }

  async function verEspejo() {
    setBusy(true);
    try {
      const reframe = await api(`/api/usuarios/${user.id_usuario}/mirror/reframe`, { method: "POST", body: { quote: patron.quote, turns } });
      localStorage.setItem("climb_mirror_reframe", JSON.stringify(reframe));
      router.push("/mirror/espejo");
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  }

  async function dejar() {
    try {
      await api(`/api/usuarios/${user.id_usuario}/mirror/dejar`, {
        method: "POST",
        body: { id: patron.id, quote: patron.quote, source: patron.source, scout_ref: patron.scout_ref, turns },
      });
    } catch {
      /* no bloquear la salida */
    }
    router.push("/mirror");
  }

  if (!user || !patron) return null;

  const respondidas = turns.filter((t) => t[0] === "user").length;
  const puedeCerrar = listo || respondidas >= 3;

  if (boundary) {
    return (
      <main>
        <h2>Mirror responds</h2>
        <p>What you&apos;re sharing is important, and that&apos;s exactly why I&apos;m not the one who should be with you there.</p>
        <p className="muted">For what you&apos;re going through, a mental health professional will be more useful than me.</p>
        <div className="row">
          <button className="btn" style={{ marginTop: 0 }} onClick={() => router.push("/mirror")}>End the session</button>
          <button className="link" onClick={() => { setBoundary(false); fetchPregunta(user, patron.quote, turns, true); }}>
            Back to the pattern →
          </button>
        </div>
      </main>
    );
  }

  return (
    <main>
      <Link className="link" href="/mirror">← Mirror</Link>
      <p className="muted" style={{ marginTop: 16 }}>Pattern · {patron.quote}</p>
      <h1>Question {respondidas + 1}</h1>
      <p className="pivote">{busy && !pregunta ? "Mirror is preparing your question…" : pregunta}</p>

      {error && <p className="error">{error}</p>}

      <div className="row">
        <input value={respuesta} onChange={(e) => setRespuesta(e.target.value)}
               onKeyDown={(e) => e.key === "Enter" && responder()}
               placeholder="Tell Mirror about your work..." />
        <button className="btn" style={{ marginTop: 0 }} disabled={busy} onClick={responder}>Send</button>
      </div>

      <div className="row" style={{ marginTop: 20 }}>
        {puedeCerrar && (
          <button className="btn" style={{ marginTop: 0 }} disabled={busy} onClick={verEspejo}>End & see the mirror →</button>
        )}
        <button className="link" onClick={dejar}>Leave for later</button>
      </div>
    </main>
  );
}
