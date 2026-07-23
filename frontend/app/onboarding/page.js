"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, getUsuario } from "../../lib/api";

const ACTOS = [
  ["Act I — Where you are today", [
    "How do you feel about your career right now? Not what others see, but what you really feel.",
    "When something at work frustrates you or you feel stuck, what do you do with it?",
  ]],
  ["Act II — Where you come from", [
    "Tell me what you do today. Your job, what kind of company, your day-to-day responsibilities.",
    "And to get there, what did you go through? Your path so far, like you'd tell it over dinner.",
  ]],
  ["Act III — What you've built", [
    "What's the achievement you're most proud of? What happened and why does that one matter?",
    "When you present in front of important people, how do you experience it? Does it lift you or weigh on you?",
  ]],
  ["Act IV — Where you're headed", [
    "What have you tried to grow or get noticed more? Tell me what didn't work too.",
    "Picture your career in three years, with no limits. What does it look like?",
    "Before we wrap up, is there anything about your career you're carrying that you haven't said?",
  ]],
];

// Aplana a 9 preguntas con su acto.
const PREGUNTAS = ACTOS.flatMap(([acto, qs]) => qs.map((q) => ({ acto, q })));

export default function Onboarding() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [paso, setPaso] = useState(0);
  const [resp, setResp] = useState(Array(9).fill(""));
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const u = getUsuario();
    if (!u) router.push("/login");
    else setUser(u);
  }, [router]);

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

  return (
    <main>
      <p className="muted" style={{ textTransform: "uppercase", fontSize: 12 }}>
        Question {String(paso + 1).padStart(2, "0")} / {PREGUNTAS.length}
      </p>
      <h2 style={{ marginTop: 4 }}>{p.acto}</h2>
      <p className="pivote" style={{ marginTop: 8 }}>{p.q}</p>
      <textarea value={resp[paso]} onChange={(e) => set(paso, e.target.value)}
                placeholder="Write the way you talk, no filter..." style={{ minHeight: 120 }} />
      {error && <p className="error">{error}</p>}
      <div className="row">
        {paso > 0 && <button className="link" onClick={() => setPaso(paso - 1)}>← Previous</button>}
        {!ultima ? (
          <button className="btn" style={{ marginTop: 0 }} onClick={() => setPaso(paso + 1)}>Next →</button>
        ) : (
          <button className="btn" style={{ marginTop: 0 }} disabled={busy} onClick={finalizar}>
            {busy ? "Generating your diagnosis…" : "Reach the summit →"}
          </button>
        )}
      </div>
    </main>
  );
}
