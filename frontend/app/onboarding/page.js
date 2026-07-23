"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, getUsuario } from "../../lib/api";

const PREGUNTAS = [
  ["apertura_emocional", "How do you feel about your career right now?"],
  ["contexto_profesional", "What do you do today? Job, company, day-to-day."],
  ["logro_principal", "The achievement you're most proud of, and why."],
  ["reaccion_presion_visibilidad", "Presenting in front of important people: does it lift you or weigh on you?"],
  ["intentos_previos", "What have you tried to grow or get noticed? What didn't work?"],
  ["vision_futuro", "Your career in three years, with no limits. What does it look like?"],
  ["desahogo_libre", "Anything about your career you're carrying that you haven't said?"],
];

export default function Onboarding() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [form, setForm] = useState({});
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [diag, setDiag] = useState(null);

  useEffect(() => {
    const u = getUsuario();
    if (!u) router.push("/login");
    else setUser(u);
  }, [router]);

  const upd = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await api(`/api/usuarios/${user.id_usuario}/perfil`, { method: "POST", body: form });
      const d = await api(`/api/usuarios/${user.id_usuario}/diagnostico`, { method: "POST" });
      // Guardamos el diagnóstico para que la pantalla de caminos lo use sin regenerarlo.
      localStorage.setItem("climb_diagnostico", JSON.stringify(d));
      setDiag(d);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  if (!user) return null;

  if (diag) {
    const patrones = diag.patrones || [];
    return (
      <main>
        <h2>Scout &middot; Your diagnosis</h2>
        <p className="pivote">{diag.frase_pivote || "Your diagnosis is ready."}</p>
        {patrones.length > 0 && (
          <>
            <h2>Patterns Scout detected</h2>
            {patrones.map((p, i) => (
              <div className="card" key={i}>
                <strong>{p.nombre}</strong>
                <p className="muted">{p.descripcion}</p>
              </div>
            ))}
          </>
        )}
        <button className="btn" onClick={() => router.push("/caminos")}>
          See my plan for the next 30 days →
        </button>
      </main>
    );
  }

  return (
    <main>
      <h1>Initial diagnosis</h1>
      <p className="sub">Write the way you talk. There are no right answers.</p>
      <form onSubmit={submit}>
        {PREGUNTAS.map(([k, q]) => (
          <div key={k}>
            <label>{q}</label>
            <textarea value={form[k] || ""} onChange={upd(k)} />
          </div>
        ))}
        {error && <p className="error">{error}</p>}
        <button className="btn" disabled={busy}>{busy ? "Generating your diagnosis…" : "Finish"}</button>
      </form>
    </main>
  );
}
