"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, getUsuario } from "../../../lib/api";
import { t, getLang } from "../../../lib/i18n";

export default function MirrorEspejo() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [lang, setLang] = useState("en");
  const [patron, setPatron] = useState(null);
  const [reframe, setReframe] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const u = getUsuario();
    if (!u) { router.push("/login"); return; }
    setUser(u); setLang(getLang());
    try {
      setPatron(JSON.parse(localStorage.getItem("climb_mirror_patron")));
      setReframe(JSON.parse(localStorage.getItem("climb_mirror_reframe")));
    } catch { router.push("/mirror"); }
  }, [router]);

  const tr = (k) => t(k, lang);

  async function resono() {
    setBusy(true);
    try {
      await api(`/api/usuarios/${user.id_usuario}/mirror/procesar`, {
        method: "POST", body: { id: patron.id, quote: patron.quote, source: patron.source, scout_ref: patron.scout_ref, reframe },
      });
      router.push("/mirror");
    } catch (err) { setError(err.message); setBusy(false); }
  }

  if (!user || !patron || !reframe) return null;

  return (
    <main>
      <p className="muted" style={{ marginTop: 16, textTransform: "uppercase", fontSize: 12 }}>{tr("the_mirror")}</p>
      <h1>{tr("this_is_what_we_saw")}</h1>
      <div className="card">
        <p className="muted" style={{ textDecoration: "line-through", margin: 0 }}>{reframe.old_quote}</p>
        <p className="pivote" style={{ color: "var(--amber)" }}>{reframe.new_quote}</p>
      </div>
      {reframe.lo_que_vimos && (<><h2>{tr("what_we_saw")}</h2><p>{reframe.lo_que_vimos}</p></>)}
      {reframe.manifestacion && (<><h2>{tr("how_shows_up")}</h2><p>{reframe.manifestacion}</p></>)}
      {(reframe.recomendaciones || []).length > 0 && (
        <><h2>{tr("recommendations")}</h2><ul>{reframe.recomendaciones.map((r, i) => <li key={i}>{r}</li>)}</ul></>
      )}
      {error && <p className="error">{error}</p>}
      <div className="row">
        <button className="btn" style={{ marginTop: 0 }} disabled={busy} onClick={resono}>{tr("resonated")}</button>
        <button className="link" onClick={() => router.push("/mirror/session")}>{tr("keep_exploring")}</button>
        <button className="link" onClick={() => router.push("/mirror")}>{tr("didnt_resonate")}</button>
      </div>
    </main>
  );
}
