import React, { useState, useMemo } from "react";

/* =========================================================================
   Understanding Your Scan — Task 6 (v4)
   AUDIENCE-SEPARATED, because a computed probability of a patient's own death
   (suspicion x outcome) is clinician/decision-analytic reasoning, NOT something
   to display to a patient.
     • Patient view (default): radiation icon array + qualitative urgency +
       "different kinds of risk" + see your doctor. No death %, no arithmetic.
     • Clinician view: full pre-test-probability decision model (radiation LAR,
       expected harm, ratio, three-scenario read) with assumptions + DATA/LIT.
   Core is deterministic (works with no network); Claude is an optional layer.
   Educational — NOT medical advice.
   ========================================================================= */

const AGES = [0, 5, 10, 15, 20, 30, 40, 50, 60, 70, 80];
const SOLID = {
  M: [2563, 2114, 1737, 1431, 1177, 798, 567, 421, 290, 162, 50],
  F: [4777, 3929, 3232, 2660, 2189, 1495, 1056, 738, 470, 246, 73],
};
const LEUK = {
  M: [237, 149, 120, 105, 96, 84, 84, 84, 82, 73, 48],
  F: [185, 112, 86, 76, 71, 63, 62, 62, 57, 51, 37],
};
function interp(arr, age) {
  if (age <= AGES[0]) return arr[0];
  if (age >= AGES[AGES.length - 1]) return arr[arr.length - 1];
  for (let i = 0; i < AGES.length - 1; i++)
    if (age >= AGES[i] && age <= AGES[i + 1]) {
      const f = (age - AGES[i]) / (AGES[i + 1] - AGES[i]);
      return arr[i] + f * (arr[i + 1] - arr[i]);
    }
  return arr[arr.length - 1];
}
function radiation(age, sex, doseMSv) {
  const per100k = interp(SOLID[sex], age) + interp(LEUK[sex], age);
  const frac = (per100k / 1e5) * (doseMSv / 100);
  return { pct: frac * 100, oneInN: frac > 0 ? Math.round(1 / frac) : Infinity, per1000: frac * 1000 };
}
const BASELINE_PER_1000 = 400;

const SUSPICION = [
  { key: "low", label: "Low", pct: 5, patient: "unlikely, but worth ruling out" },
  { key: "moderate", label: "Moderate", pct: 30, patient: "a real possibility" },
  { key: "high", label: "High", pct: 70, patient: "likely" },
];

const CONDS = {
  appendicitis: {
    label: "Appendicitis (a swollen appendix)", scan: "CT scan of the belly & pelvis", dose: 10,
    stakes: "Appendicitis is very treatable, but finding it late lets the appendix burst — causing infection, an abscess, and a harder recovery.",
    timeline: "The chance of a burst appendix rises about 2% for every hour of delay, and a missed diagnosis makes a burst about 3 times more likely.",
    compare: null, excess: null, harmWord: "a burst appendix and its complications",
    figures: [
      { t: "Perforation odds rise ~2% per hour of delay", s: "PMID 27749630", tag: "DATA" },
      { t: "Missed diagnosis → ~3× higher chance of a burst (aOR 3.1)", s: "PMID 37355425", tag: "DATA" },
    ],
  },
  ischemic_stroke: {
    label: "A stroke (blocked vessel in the brain)", scan: "CT scan of the head", dose: 2,
    stakes: "In a stroke, brain tissue dies every minute. A scan rapidly shows whether it's a clot or a bleed — and the two need opposite treatments, so getting it right fast is vital.",
    timeline: "Untreated, the brain loses about 1.9 million cells a minute, and the benefit of treatment fades within hours (+26% better recovery at 3 h falls to +7% by 6 h).",
    compare: null, excess: null, harmWord: "lasting disability",
    figures: [
      { t: "~1.9 million brain cells lost per minute untreated", s: "Saver 2006", tag: "LIT" },
      { t: "Each hour of delay lowers the odds of a good recovery", s: "PMID 27673305", tag: "DATA" },
      { t: "Recovery benefit: +26% (3 h) → +7% (6 h)", s: "PMID 26716735", tag: "DATA" },
    ],
  },
  pulmonary_embolism: {
    label: "A blood clot in the lungs (PE)", scan: "CT scan of the chest", dose: 15,
    stakes: "A blood clot in the lungs can be serious — but it is very treatable when found in time.",
    timeline: "A delayed diagnosis raises the risk of dying about three-fold.",
    compare: { early: 2, delayed: 43, verb: "die in hospital", src: "PMID 32694258", tag: "DATA" },
    excess: { pct: 41, outcome: "death in hospital", basis: "43% delayed − 2% early", tag: "DATA" }, harmWord: "death",
    figures: [
      { t: "Caught early ~2 in 100 die in hospital; delayed ~43 in 100", s: "PMID 32694258", tag: "DATA" },
      { t: "Delayed diagnosis → ~3× higher 30-day death rate (RR 3.31)", s: "PMID 41004149", tag: "DATA" },
    ],
  },
  aortic_dissection: {
    label: "A tear in the aorta (aortic dissection)", scan: "CT scan of the chest & belly", dose: 16,
    stakes: "A tear in the body's main artery is an immediate, life-threatening emergency.",
    timeline: "Untreated, the risk of dying climbs roughly 1–2% every hour — about half of people die within two days without treatment.",
    compare: null, excess: { pct: 50, outcome: "death within ~2 days", basis: "untreated natural history, ~1–2%/h", tag: "LIT" }, harmWord: "death",
    figures: [
      { t: "Untreated mortality rises ~1–2% per hour over the first two days", s: "IRAD / Hirsch 2010", tag: "LIT" },
      { t: "Direct delay-vs-outcome data from primary studies are sparse — a gap this project documents", s: "Task 2", tag: "DATA" },
    ],
  },
  mesenteric_ischemia: {
    label: "Blocked blood flow to the intestines", scan: "CT scan of the belly", dose: 12,
    stakes: "Blocked blood flow to the intestines is among the most dangerous abdominal emergencies — survival depends on acting fast.",
    timeline: "Even with prompt surgery this is often serious, and delay beyond a day worsens the odds further.",
    compare: { early: 72, delayed: 87, verb: "die", src: "PMID 16796010", tag: "DATA" },
    excess: { pct: 15, outcome: "death", basis: "87% (delayed) − 72% (early)", tag: "DATA" }, harmWord: "death",
    figures: [
      { t: "Surgery within 24 h ~72 in 100 die; after 24 h ~87 in 100", s: "PMID 16796010", tag: "DATA" },
      { t: "Surgical consult delayed past 24 h → ~9× higher odds of dying", s: "PMID 19350855", tag: "DATA" },
    ],
  },
  subarachnoid_hemorrhage: {
    label: "Bleeding around the brain", scan: "CT scan of the head", dose: 2,
    stakes: "A scan rapidly finds bleeding around the brain, which can be immediately life-threatening if missed.",
    timeline: "Solid figures on the exact harm of delay are limited — a real evidence gap — but the danger of a missed brain bleed is well recognized, and a re-bleed can be devastating.",
    compare: null, excess: null, harmWord: "a dangerous re-bleed",
    figures: [
      { t: "Outcome studies rarely quantify the harm of delay here — the evidence is sparse (a finding)", s: "Task 2", tag: "DATA" },
      { t: "Commonly cited figures (≈1 in 5 initially missed) come from reviews, not primary studies", s: "manuscript", tag: "LIT" },
    ],
  },
  major_trauma: {
    label: "Serious injuries after an accident", scan: "whole-body CT scan", dose: 20,
    stakes: "After a serious accident, hidden internal injuries can be life-threatening. A whole-body scan finds them fast.",
    timeline: "Patients given a whole-body scan have about a 20–25% higher chance of survival than those assessed with older methods.",
    compare: null, excess: { pct: 22, outcome: "death", basis: "whole-body CT survival benefit ~20–25%", tag: "LIT" }, harmWord: "death from a missed injury",
    figures: [
      { t: "Whole-body CT improves probability of survival ~20–25% vs prior methods (review)", s: "PMID 25216568", tag: "LIT" },
    ],
  },
};
const ORDER = ["appendicitis", "ischemic_stroke", "pulmonary_embolism", "aortic_dissection", "mesenteric_ischemia", "subarachnoid_hemorrhage", "major_trauma"];

function scenarioFor(ratio) {
  if (ratio == null) return null;
  if (ratio >= 10) return { tag: "Scenario 1", line: "the risk of not scanning clearly outweighs the radiation", tone: "harm" };
  if (ratio >= 2) return { tag: "Scenario 1 (less extreme)", line: "not scanning still looks riskier than the radiation, though less overwhelmingly", tone: "harm" };
  if (ratio >= 0.5) return { tag: "Scenario 3", line: "the two risks are in a similar range — a genuine judgment call", tone: "bal" };
  return { tag: "Scenario 2", line: "the scan's radiation risk may rival the benefit — worth careful discussion", tone: "rad" };
}

function IconArray({ added }) {
  const dots = useMemo(() => {
    const out = [];
    for (let i = 0; i < 1000; i++) {
      let cls = "d-empty";
      if (i < added) cls = "d-add";
      else if (i < added + BASELINE_PER_1000) cls = "d-base";
      out.push(<span key={i} className={"dot " + cls} />);
    }
    return out;
  }, [added]);
  return <div className="grid">{dots}</div>;
}

export default function UnderstandingYourScan() {
  const [audience, setAudience] = useState("patient");
  const [age, setAge] = useState(55);
  const [sex, setSex] = useState("F");
  const [condKey, setCondKey] = useState("pulmonary_embolism");
  const [suspKey, setSuspKey] = useState("moderate");
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [reply, setReply] = useState("");
  const [askMsg, setAskMsg] = useState("");

  const isClin = audience === "clinician";
  const cond = CONDS[condKey];
  const susp = SUSPICION.find((s) => s.key === suspKey);
  const rad = radiation(age, sex, cond.dose);
  const added = Math.max(1, Math.round(rad.per1000));
  const radPct = rad.pct;
  const radTxt = radPct >= 1 ? radPct.toFixed(1) : radPct >= 0.1 ? radPct.toFixed(2) : radPct.toFixed(3);
  const bgYears = Math.round(cond.dose / 3);
  const ageWord = age <= 17 ? "child" : age >= 65 ? "older adult" : "adult";

  const expected = cond.excess ? (susp.pct / 100) * cond.excess.pct : null;
  const ratio = expected != null ? expected / Math.max(radPct, 1e-9) : null;
  const scn = scenarioFor(ratio);

  const summary = useMemo(() => {
    const who = `${age}-year-old ${sex === "F" ? "woman" : "man"}`;
    if (!isClin) {
      let s = `A ${cond.scan.toLowerCase()} uses about ${cond.dose} mSv of radiation — roughly ${bgYears} year${bgYears === 1 ? "" : "s"} of natural background. For a ${who}, that adds only about ${radTxt}% to the lifetime chance of cancer (about ${added} in 1,000 people, on top of the ~400 in 1,000 who develop cancer anyway) — a small addition. `;
      s += `${cond.stakes} ${cond.timeline} `;
      s += `Right now your doctor considers this ${susp.patient}. When a problem like this is found and treated early, the great majority of people do well — the real risk is in missing or delaying it. `;
      s += `So the scan's radiation is a small, long-term risk, while the condition is an immediate and treatable one. Whether you need the scan depends on your full picture, so decide together with your doctor.`;
      return s;
    }
    let s = `${who}; suspected ${cond.label}. ${cond.scan} ≈ ${cond.dose} mSv → BEIR VII LAR ≈ ${radTxt}% (1 in ${rad.oneInN.toLocaleString()}), incidence, all-solid + leukemia. `;
    if (expected != null) {
      const cmp = ratio >= 10 ? "far exceeds" : ratio >= 2 ? "exceeds" : ratio >= 0.5 ? "is comparable to" : "is below";
      s += `Expected harm of not scanning = pre-test ${susp.pct}% × ${cond.excess.pct}% (${cond.excess.basis}) ≈ ${expected.toFixed(1)}% ${cond.excess.outcome}, which ${cmp} the ${radTxt}% radiation LAR (ratio ≈ ${ratio >= 10 ? Math.round(ratio) : ratio.toFixed(1)}×). ${scn.tag}: ${scn.line}.`;
    } else {
      s += `No clean conditional outcome rate available for an expected-harm estimate here (harm is ${cond.harmWord}${condKey === "subarachnoid_hemorrhage" ? "; primary-abstract data sparse" : ""}); weigh the qualitative urgency against the small LAR.`;
    }
    return s;
  }, [audience, age, sex, condKey, suspKey]);

  async function askClaude() {
    setLoading(true); setAskMsg(""); setReply("");
    const instr = isClin
      ? "You are a concise clinical decision-support assistant for a physician. Use ONLY the facts below; never invent statistics. ~140-180 words. You may discuss the expected-harm/pre-test reasoning. Remain non-directive about the final decision, note key uncertainties (effective dose as whole-body proxy; LNT; population-level outcome data), and defer to clinical judgement and guidelines."
      : "You are a warm, plain-spoken health educator. You are NOT the patient's doctor and must never tell them what to do or whether to have the scan, and must NOT state a personalized probability of their death. Use ONLY the facts below; never invent statistics. Write at a 7th-8th grade level, calm and honest, ~150-180 words. Reassure that the radiation risk is small and far-off while the condition is an immediate, treatable concern; explain why timely diagnosis matters in general terms. Answer their question gently. Always end by encouraging them to decide together with their own doctor.";
    const facts =
      `FACTS:\n` +
      `- Patient: ${age}-year-old ${sex === "F" ? "woman" : "man"} (an ${ageWord}).\n` +
      `- Possible condition: ${cond.label}; checked with a ${cond.scan}.\n` +
      `- Radiation: ~${added} in 1,000 scanned at this age/sex develop a scan-caused cancer over life (~${radTxt}%); ~400 in 1,000 get cancer regardless; dose ≈ ${bgYears} yr background; lower with age, higher for children.\n` +
      `- Why timely diagnosis matters: ${cond.stakes} ${cond.timeline}\n` +
      (isClin && cond.compare ? `- Outcomes (population-level): ~${cond.compare.early}/100 ${cond.compare.verb} early vs ~${cond.compare.delayed}/100 delayed.\n` : "") +
      (isClin && expected != null ? `- Expected harm of not scanning ≈ ${susp.pct}% × ${cond.excess.pct}% ≈ ${expected.toFixed(1)}% ${cond.excess.outcome}; vs ${radTxt}% LAR; ${scn.tag}.\n` : "") +
      (!isClin ? `- The doctor currently considers this ${susp.patient}.\n` : "") +
      (question.trim() ? `\nQuestion: "${question.trim()}"` : "\nNo specific question — give a brief explanation.");
    try {
      const res = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ model: "claude-sonnet-4-20250514", max_tokens: 1000, messages: [{ role: "user", content: instr + "\n\n" + facts }] }),
      });
      if (!res.ok) throw new Error(res.status);
      const data = await res.json();
      const text = (data.content || []).filter((b) => b.type === "text").map((b) => b.text).join("\n").trim();
      if (text) setReply(text); else setAskMsg("No answer came back — the summary above still applies.");
    } catch (e) {
      setAskMsg("Live AI answers aren't available in this view (they need the hosted app). The summary above already explains the situation.");
    } finally { setLoading(false); }
  }

  const Tag = ({ k }) => <span className={"tag " + (k === "DATA" ? "t-data" : "t-lit")}>{k}</span>;

  return (
    <>
      <style>{CSS}</style>
      <div className="uys">
        <header className="head">
          <div className="head-row">
            <div className="kicker">{isClin ? "Decision support · radiation vs the risk of not scanning" : "A guide to talk through with your doctor"}</div>
            <div className="aud">
              {["patient", "clinician"].map((a) => <button key={a} className={audience === a ? "on" : ""} onClick={() => setAudience(a)}>{a === "patient" ? "Patient" : "Clinician"}</button>)}
            </div>
          </div>
          <h1>Understanding your scan</h1>
          <p className="sub">{isClin
            ? <>An estimate of the trade-off between a CT's radiation risk and the expected harm of not scanning, weighted by pre-test probability. Point estimates with real uncertainty — an aid to judgement, not a rule.</>
            : <>A CT scan uses a small amount of radiation. For some urgent problems, the bigger risk is <i>not</i> getting the scan in time. Here's what that means for your situation, in plain terms.</>}
          </p>
        </header>

        <section className="form">
          <div className="field"><label>{isClin ? "Patient age" : "Your age"}: <b>{age}</b></label>
            <input type="range" min="0" max="80" value={age} onChange={(e) => setAge(+e.target.value)} /></div>
          <div className="row2">
            <div className="field"><label>Sex</label>
              <div className="seg">{["F", "M"].map((s) => <button key={s} className={sex === s ? "on" : ""} onClick={() => setSex(s)}>{s === "F" ? "Female" : "Male"}</button>)}</div></div>
            <div className="field grow"><label>{isClin ? "Suspected condition" : "What did your doctor mention?"}</label>
              <select value={condKey} onChange={(e) => setCondKey(e.target.value)}>{ORDER.map((k) => <option key={k} value={k}>{CONDS[k].label}</option>)}</select></div>
          </div>
          <div className="field"><label>{isClin ? "Pre-test probability (clinical suspicion)" : "How strongly is it suspected?"} <span className="opt">{isClin ? "(clinician estimate)" : "(your doctor's judgment)"}</span></label>
            <div className="seg susp">{SUSPICION.map((s) => <button key={s.key} className={suspKey === s.key ? "on" : ""} onClick={() => setSuspKey(s.key)}>{s.label}<em>~{s.pct}%</em></button>)}</div>
          </div>
        </section>

        {/* ---------- CLINICIAN: full decision model ---------- */}
        {isClin && (
          <section className="decision">
            <div className="dec-grid">
              <div className="dec-col"><div className="dec-h">Radiation risk of scanning</div><div className="dec-num">{radTxt}<span>%</span></div><div className="dec-cap">BEIR VII LAR · ~1 in {rad.oneInN.toLocaleString()}</div></div>
              <div className="dec-mid">{ratio != null ? <span className="dec-ratio">{ratio >= 10 ? Math.round(ratio) : ratio.toFixed(1)}×<em>expected-harm : LAR</em></span> : <span className="dec-vs">vs</span>}</div>
              <div className="dec-col"><div className="dec-h">Expected harm of not scanning</div>
                {expected != null ? <>
                  <div className="dec-num h">{expected.toFixed(1)}<span>%</span></div>
                  <div className="dec-cap">{susp.pct}% pre-test × {cond.excess.pct}% {cond.excess.outcome} <Tag k={cond.excess.tag} /></div>
                </> : <><div className="dec-num h small">not quantified</div><div className="dec-cap">no clean conditional rate ({cond.harmWord})</div></>}
              </div>
            </div>
            {scn && <div className={"scenario s-" + scn.tone}><b>{scn.tag}:</b> {scn.line}.</div>}
            <p className="dec-text">{summary}</p>
            <p className="assume">Assumptions: effective dose treated as whole-body-equivalent for LAR; LNT at low dose; outcome rates are population-level (not patient-adjusted); expected harm = pre-test × delay-attributable excess. Not a substitute for guidelines (e.g., ACR Appropriateness Criteria) or clinical judgement.</p>
          </section>
        )}

        {/* ---------- PATIENT: calm, no death math ---------- */}
        {!isClin && (
          <section className="patient-sum">
            <div className="ps-row">
              <span className="ps-pill rad-pill">Radiation from the scan: small — about {radTxt}%, roughly 1 in {rad.oneInN.toLocaleString()}, added to your lifetime cancer chance</span>
              <span className="ps-pill harm-pill">This condition is {susp.patient} and {condKey === "appendicitis" || condKey === "major_trauma" ? "time-sensitive" : "urgent"} — finding it early matters a lot</span>
            </div>
            <p className="dec-text">{summary}</p>
          </section>
        )}

        {/* ---------- DETAIL PANELS ---------- */}
        <section className="panels">
          <div className="panel rad">
            <div className="p-top"><span className="d dr" /><h2>The radiation, in people</h2></div>
            <div className="p-proto">{cond.scan} · about {cond.dose} mSv (≈ {bgYears} year{bgYears === 1 ? "" : "s"} of background radiation)</div>
            <IconArray added={added} />
            <div className="legend">
              <span><i className="sw d-add" /> Extra cancer from this scan — about <b>{added}</b> in 1,000</span>
              <span><i className="sw d-base" /> Cancer in their lifetime regardless — about 400 in 1,000</span>
              <span><i className="sw d-empty" /> No cancer</span>
            </div>
            <p className="takeaway">{age >= 65 ? "At an older age this risk is small — radiation-caused cancers take many years to appear." : age <= 17 ? "For a child this is higher than for an adult — more years ahead for a cancer to develop." : "The risk is lower the older you are, and higher for children."} <span className="muted">Personalized by age, sex, and scan dose.</span></p>
          </div>

          <div className="panel harm">
            <div className="p-top"><span className="d dh" /><h2>Why finding it fast matters</h2></div>
            <p className="stakes">{cond.stakes}</p>
            {isClin && cond.compare && (
              <div className="cmp">
                <div className="cmp-row"><span className="cmp-lab">Caught early</span><div className="cmp-bar"><div className="cmp-fill early" style={{ width: cond.compare.early + "%" }} /></div><span className="cmp-val">~{cond.compare.early} in 100 {cond.compare.verb}</span></div>
                <div className="cmp-row"><span className="cmp-lab">Diagnosis delayed</span><div className="cmp-bar"><div className="cmp-fill delayed" style={{ width: cond.compare.delayed + "%" }} /></div><span className="cmp-val">~{cond.compare.delayed} in 100 {cond.compare.verb}</span></div>
                <div className="cmp-src"><Tag k={cond.compare.tag} /> {cond.compare.src} · population-level, not patient-adjusted</div>
              </div>
            )}
            <div className="timeline"><span className="clock">⏱</span><span>{cond.timeline}</span></div>
            {isClin ? (
              <ul className="figs">{cond.figures.map((f, i) => <li key={i}><span>{f.t}</span> <Tag k={f.tag} /> <span className="src">{f.s}</span></li>)}</ul>
            ) : (
              <p className="figs-note">When caught and treated early, most people do well — which is why doctors don't wait when this is a real possibility. Your care team weighs the detailed outcome studies behind this.</p>
            )}
          </div>
        </section>

        {/* ---------- OPTIONAL Q&A ---------- */}
        <section className="ask">
          <div className="ask-h">{isClin ? "Ask a question (decision-support)" : "Have a question, or want it in plainer words?"}</div>
          <textarea rows={2} value={question} placeholder={isClin ? "e.g. how sensitive is the scenario to a 50% pre-test probability?" : "e.g. I'm scared of radiation — is one scan dangerous? Can I wait a day?"} onChange={(e) => setQuestion(e.target.value)} />
          <button className="go" onClick={askClaude} disabled={loading}>{loading ? "Thinking it through…" : "Ask in plain language"}</button>
          {loading && <div className="thinking"><span /><span /><span /></div>}
          {askMsg && <div className="ask-note">{askMsg}</div>}
          {reply && (<div className="reply"><div className="ex-body">{reply.split("\n").filter(Boolean).map((p, i) => <p key={i}>{p}</p>)}</div><div className="byline">Plain-language answer by Claude, using only the figures shown above.</div></div>)}
        </section>

        <footer className="disclaimer">
          <b>General information, not medical advice.</b> It cannot tell you whether to have a scan — your doctor knows your full health, history, and situation, so decide together. If you may be having an emergency, call your local emergency number.
          <div className="srcline">Radiation — BEIR VII Phase 2, Table 12D-1 (NRC 2006) &amp; Mettler et al., Radiology 2008. Harms — studies in this project (PMIDs shown). {isClin ? "Expected harm = pre-test probability × delay-attributable outcome gap. " : ""}<Tag k="DATA" /> measured in a study · <Tag k="LIT" /> wider-literature figure.</div>
        </footer>
      </div>
    </>
  );
}

const CSS = `
@import url('https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&family=IBM+Plex+Sans:wght@400;450;500;600&display=swap');
.uys{--bg:#F2EFE7;--ink:#262219;--mut:#6d6759;--line:#e2ddd0;--card:#fcfbf7;
 --calm:#3a7c8a;--calm-soft:#dde9ec;--warm:#b5613e;--warm-soft:#f1e1d8;--alarm:#9d3b29;
 font-family:'IBM Plex Sans',sans-serif;color:var(--ink);
 background:radial-gradient(130% 90% at 100% 0%, #f8f6f0 0%, var(--bg) 60%);
 max-width:900px;margin:0 auto;padding:30px 26px 22px;line-height:1.55;}
.uys *{box-sizing:border-box;}
.head-row{display:flex;justify-content:space-between;align-items:flex-start;gap:14px;margin-bottom:9px;}
.kicker{font-size:11.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--calm);font-weight:600;padding-top:4px;}
.aud{display:flex;border:1px solid var(--line);border-radius:9px;overflow:hidden;flex-shrink:0;background:#fff;}
.aud button{border:none;background:#fff;padding:6px 14px;font:inherit;font-size:12.5px;cursor:pointer;color:var(--mut);transition:.15s;}
.aud button.on{background:var(--ink);color:#fff;font-weight:500;}
.head h1{font-family:'Newsreader',serif;font-weight:500;font-size:37px;line-height:1.04;margin:0 0 10px;letter-spacing:-.01em;}
.sub{color:var(--mut);font-size:15px;max-width:680px;margin:0;} .sub i{font-style:italic;color:var(--warm);font-weight:500;}

.form{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:22px 24px;margin:22px 0 16px;display:flex;flex-direction:column;gap:15px;}
.field{display:flex;flex-direction:column;gap:8px;}
.field label{font-size:13.5px;color:var(--ink);font-weight:500;} .field label b{font-variant-numeric:tabular-nums;}
.opt{color:var(--mut);font-weight:400;font-size:12.5px;}
.row2{display:flex;gap:16px;align-items:flex-end;} .row2 .grow{flex:1;}
input[type=range]{-webkit-appearance:none;appearance:none;height:5px;border-radius:3px;background:var(--line);outline:none;}
input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:20px;height:20px;border-radius:50%;background:var(--calm);cursor:pointer;border:3px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,.18);}
input[type=range]::-moz-range-thumb{width:16px;height:16px;border-radius:50%;background:var(--calm);cursor:pointer;border:3px solid #fff;}
.seg{display:flex;border:1px solid var(--line);border-radius:10px;overflow:hidden;}
.seg button{flex:1;border:none;background:#fff;padding:9px 14px;font:inherit;font-size:14px;cursor:pointer;color:var(--mut);transition:.15s;display:flex;flex-direction:column;align-items:center;gap:1px;}
.seg.susp button em{font-style:normal;font-size:10.5px;opacity:.7;}
.seg button.on{background:var(--calm);color:#fff;font-weight:500;}
select,textarea{font:inherit;font-size:14.5px;padding:10px 12px;border:1px solid var(--line);border-radius:10px;background:#fff;color:var(--ink);width:100%;resize:vertical;}
.go{align-self:flex-start;background:var(--ink);color:#fff;border:none;border-radius:11px;padding:11px 20px;font:inherit;font-size:14.5px;font-weight:500;cursor:pointer;transition:.15s;margin-top:10px;}
.go:hover{background:#000;} .go:disabled{opacity:.6;cursor:default;}

.patient-sum{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:20px 24px;margin-bottom:16px;border-top:3px solid var(--calm);}
.ps-row{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:6px;}
.ps-pill{font-size:13px;line-height:1.4;padding:11px 14px;border-radius:11px;flex:1;min-width:240px;}
.rad-pill{background:var(--calm-soft);color:#234;} .harm-pill{background:var(--warm-soft);color:#5a3725;}
.dec-text{font-size:14.5px;line-height:1.62;color:#33302a;margin:14px 0 0;}
.patient-sum .dec-text{border-top:1px dashed var(--line);padding-top:14px;}

.decision{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:20px 24px;margin-bottom:16px;border-top:3px solid var(--ink);}
.dec-grid{display:grid;grid-template-columns:1fr auto 1fr;gap:14px;align-items:center;}
.dec-h{font-size:12px;color:var(--mut);font-weight:500;margin-bottom:7px;min-height:30px;}
.dec-num{font-family:'Newsreader',serif;font-weight:500;font-size:42px;line-height:1;color:var(--calm);font-variant-numeric:tabular-nums;}
.dec-num.h{color:var(--alarm);} .dec-num.small{font-size:21px;} .dec-num span{font-size:20px;margin-left:2px;}
.dec-cap{font-size:11.5px;color:var(--mut);margin-top:7px;line-height:1.4;}
.dec-mid{display:flex;align-items:center;justify-content:center;text-align:center;}
.dec-ratio{font-family:'Newsreader',serif;font-size:20px;color:var(--ink);font-weight:600;display:flex;flex-direction:column;line-height:1.1;}
.dec-ratio em{font-style:normal;font-size:9px;color:var(--mut);font-weight:400;letter-spacing:.03em;margin-top:2px;text-transform:uppercase;}
.dec-vs{font-family:'Newsreader',serif;font-style:italic;color:var(--mut);font-size:16px;}
.scenario{margin-top:16px;padding:10px 14px;border-radius:10px;font-size:13.5px;line-height:1.45;} .scenario b{font-weight:600;}
.s-harm{background:var(--warm-soft);color:#5a3725;} .s-bal{background:#f3ecd6;color:#5f4f1e;} .s-rad{background:var(--calm-soft);color:#234;}
.decision .dec-text{border-top:1px dashed var(--line);padding-top:14px;}
.assume{font-size:11px;color:var(--mut);line-height:1.5;margin:12px 0 0;font-style:italic;}

.panels{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:16px;align-items:start;}
.panel{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:20px 22px;}
.panel.rad{border-top:3px solid var(--calm);} .panel.harm{border-top:3px solid var(--warm);}
.p-top{display:flex;align-items:center;gap:9px;margin-bottom:5px;} .p-top h2{font-family:'Newsreader',serif;font-weight:500;font-size:19px;margin:0;}
.d{width:9px;height:9px;border-radius:50%;} .dr{background:var(--calm);} .dh{background:var(--warm);}
.p-proto{font-size:12.5px;color:var(--mut);margin-bottom:14px;}
.grid{display:flex;flex-wrap:wrap;gap:1.5px;width:100%;max-width:336px;margin:2px 0 12px;}
.dot{width:6px;height:6px;border-radius:1.5px;}
.d-empty{background:#e6e1d6;} .d-base{background:#c8c1b2;} .d-add{background:var(--alarm);}
.legend{display:flex;flex-direction:column;gap:4px;font-size:11.5px;color:var(--mut);margin-bottom:12px;} .legend b{color:var(--ink);}
.sw{display:inline-block;width:9px;height:9px;border-radius:2px;margin-right:6px;vertical-align:middle;}
.takeaway{font-size:13px;line-height:1.5;color:#33302a;margin:0;border-top:1px dashed var(--line);padding-top:12px;} .takeaway .muted{color:var(--mut);}
.stakes{font-size:15px;font-weight:450;margin:2px 0 14px;color:var(--ink);line-height:1.45;}
.cmp{background:#fff;border:1px solid var(--line);border-radius:11px;padding:13px 14px;margin-bottom:14px;display:flex;flex-direction:column;gap:9px;}
.cmp-row{display:grid;grid-template-columns:92px 1fr auto;align-items:center;gap:10px;}
.cmp-lab{font-size:12px;color:var(--mut);}
.cmp-bar{height:14px;background:#f0ece2;border-radius:7px;overflow:hidden;}
.cmp-fill{height:100%;border-radius:7px;} .cmp-fill.early{background:#7fae8a;} .cmp-fill.delayed{background:var(--alarm);}
.cmp-val{font-size:12px;font-weight:500;font-variant-numeric:tabular-nums;white-space:nowrap;} .cmp-src{font-size:10.5px;color:var(--mut);}
.timeline{display:flex;gap:9px;align-items:flex-start;background:var(--warm-soft);border-radius:10px;padding:11px 13px;font-size:13.5px;line-height:1.45;color:#5a3725;margin-bottom:14px;} .clock{font-size:15px;}
.figs{list-style:none;padding:0;margin:0;border-top:1px dashed var(--line);padding-top:12px;display:flex;flex-direction:column;gap:9px;}
.figs li{font-size:12.5px;line-height:1.4;} .src{color:var(--mut);font-size:11px;}
.figs-note{font-size:13px;line-height:1.5;color:#33302a;border-top:1px dashed var(--line);padding-top:12px;margin:0;}
.tag{font-size:9px;font-weight:700;letter-spacing:.05em;padding:1.5px 5px;border-radius:5px;vertical-align:middle;}
.t-data{background:var(--calm-soft);color:var(--calm);} .t-lit{background:#efe7d4;color:#8a6d22;}

.ask{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:20px 24px;margin-bottom:16px;}
.ask-h{font-size:14.5px;font-weight:500;margin-bottom:10px;}
.ask-note{font-size:13px;color:var(--mut);background:var(--warm-soft);border-radius:9px;padding:10px 13px;margin-top:12px;line-height:1.45;}
.reply{margin-top:14px;background:var(--calm-soft);border:1px solid #cfe0e4;border-radius:12px;padding:18px 20px;}
.ex-body p{font-size:15px;line-height:1.62;margin:0 0 11px;color:#22302f;} .ex-body p:last-child{margin-bottom:0;}
.byline{font-size:11.5px;color:var(--mut);margin-top:12px;border-top:1px dashed #cfe0e4;padding-top:9px;font-style:italic;}
.thinking{display:flex;gap:7px;padding:10px 0 2px;}
.thinking span{width:9px;height:9px;border-radius:50%;background:var(--calm);opacity:.5;animation:bnc 1.1s infinite ease-in-out;}
.thinking span:nth-child(2){animation-delay:.18s;} .thinking span:nth-child(3){animation-delay:.36s;}
@keyframes bnc{0%,80%,100%{transform:translateY(0);opacity:.4;}40%{transform:translateY(-7px);opacity:1;}}

.disclaimer{font-size:12.5px;color:var(--mut);line-height:1.55;background:var(--warm-soft);border:1px solid #e8d3c6;border-radius:13px;padding:15px 18px;} .disclaimer b{color:#7d4327;}
.srcline{margin-top:9px;padding-top:9px;border-top:1px dashed #e3cdbf;font-size:11px;}

@media(max-width:720px){
 .head h1{font-size:28px;} .head-row{flex-direction:column;}
 .panels{grid-template-columns:1fr;} .row2{flex-direction:column;align-items:stretch;gap:15px;} .grid{max-width:none;}
 .dec-grid{grid-template-columns:1fr;gap:16px;text-align:center;} .dec-h{min-height:0;} .cmp-row{grid-template-columns:84px 1fr;} .cmp-val{grid-column:2;text-align:right;}
}
`;
