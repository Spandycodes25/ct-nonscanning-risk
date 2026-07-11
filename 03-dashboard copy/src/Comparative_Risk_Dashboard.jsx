import React, { useState, useEffect, useRef } from "react";

/* =========================================================================
   Comparative Risk Dashboard  —  Task 3
   Radiation risk (BEIR VII LAR, Table 12D-1) vs non-scanning harm (Task 2).
   Sources: BEIR VII Phase 2 (NRC 2006); Mettler et al., Radiology 2008 (doses).
   Illustrative decision-framing tool, NOT for individual clinical use.
   ========================================================================= */

// --- BEIR VII Table 12D-1: LAR of cancer INCIDENCE per 100,000 per 0.1 Gy ---
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
  for (let i = 0; i < AGES.length - 1; i++) {
    if (age >= AGES[i] && age <= AGES[i + 1]) {
      const f = (age - AGES[i]) / (AGES[i + 1] - AGES[i]);
      return arr[i] + f * (arr[i + 1] - arr[i]);
    }
  }
  return arr[arr.length - 1];
}

// LAR fraction for an effective dose (mSv) and scan count.
// Table is per 100 mSv (0.1 Gy); effective dose treated as whole-body-equivalent
// for LAR scaling — the standard CT-calculator simplification.
function computeLAR(age, sex, doseMSv, nScans) {
  const per100k = interp(SOLID[sex], age) + interp(LEUK[sex], age);
  const frac = (per100k / 1e5) * (doseMSv * nScans / 100);
  return { per100k, frac, pct: frac * 100, oneInN: frac > 0 ? Math.round(1 / frac) : Infinity };
}

// --- Conditions: CT protocol + Mettler dose + non-scanning harm (Task 2) ---
const CONDS = {
  appendicitis: {
    label: "Acute appendicitis", protocol: "CT abdomen & pelvis", dose: 10, doseNote: "≈10 mSv",
    headline: "Missed or delayed diagnosis drives perforation and its complications.",
    bar: { pct: 13.6, label: "Wound infection when antibiotics delayed >4 h (vs 2.9%)", src: "PMID 32250068", tag: "DATA" },
    figures: [
      { t: "Perforation odds rise ≈2% per hour of delay (OR 1.02/h)", s: "PMID 27749630", tag: "DATA" },
      { t: "Missed diagnosis → perforation aOR 3.1; abscess aOR 3.0", s: "PMID 37355425", tag: "DATA" },
      { t: "Delayed diagnosis → perforation OR up to 7.8", s: "PMID 34463745", tag: "DATA" },
    ],
  },
  ischemic_stroke: {
    label: "Ischemic stroke", protocol: "CT head ± CT angiography", dose: 2, doseNote: "≈2 mSv (CTA adds ~5)",
    headline: "Time is brain — every hour of delay erases treatment benefit.",
    bar: { pct: 25.9, label: "Good-outcome benefit (mRS 0–2) foregone if reperfusion slips to 3 h+", src: "PMID 26716735", tag: "DATA" },
    figures: [
      { t: "Each 1-h delay to reperfusion: disability cOR 0.84", s: "PMID 27673305", tag: "DATA" },
      { t: "Reperfusion benefit decays +25.9% (3 h) → +6.7% (6 h)", s: "PMID 26716735", tag: "DATA" },
      { t: "Untreated large-vessel stroke loses ~1.9M neurons/min", s: "Saver 2006", tag: "LIT" },
    ],
  },
  subarachnoid_hemorrhage: {
    label: "Subarachnoid hemorrhage", protocol: "CT head (non-contrast)", dose: 2, doseNote: "≈2 mSv",
    headline: "Primary-abstract delay-harm data are sparse (a finding) — yet a missed SAH risks catastrophic rebleeding.",
    bar: null, sparse: true,
    figures: [
      { t: "Outcome-focused abstract search yielded ~no extractable delay-harm estimates", s: "Task 2", tag: "DATA" },
      { t: "Synthesized SAH figures (≈19% initially missed; high rebleed mortality) live in reviews, not primary abstracts", s: "manuscript", tag: "LIT" },
    ],
  },
  pulmonary_embolism: {
    label: "Pulmonary embolism", protocol: "CT pulmonary angiography", dose: 15, doseNote: "≈15 mSv (13–40)",
    headline: "Delayed diagnosis multiplies mortality several-fold.",
    bar: { pct: 43.2, label: "In-hospital mortality if diagnosis delayed (vs 1.6% early)", src: "PMID 32694258", tag: "DATA" },
    figures: [
      { t: "30-day mortality RR 3.31 (delayed vs timely diagnosis)", s: "PMID 41004149", tag: "DATA" },
      { t: "In-hospital mortality 1.6% (early) vs 43.2% (delayed)", s: "PMID 32694258", tag: "DATA" },
    ],
  },
  aortic_dissection: {
    label: "Aortic dissection", protocol: "CT angiography (chest/abdomen)", dose: 16, doseNote: "≈16 mSv",
    headline: "Untreated type-A dissection kills ~1–2% of patients per hour.",
    bar: { pct: 67, label: "Cumulative mortality by 48 h untreated (~1.4%/h)", src: "IRAD / Hirsch 2010", tag: "LIT" },
    figures: [
      { t: "Mortality accrues ~1–2% per hour in the first 48 h", s: "IRAD / Hirsch 2010", tag: "LIT" },
      { t: "Primary-abstract delay-harm estimates were absent from extraction (a finding)", s: "Task 2", tag: "DATA" },
    ],
  },
  mesenteric_ischemia: {
    label: "Mesenteric ischemia", protocol: "CT angiography (abdomen/pelvis)", dose: 12, doseNote: "≈12 mSv",
    headline: "Lethal even when prompt; delay pushes mortality higher still.",
    bar: { pct: 87, label: "Mortality if surgery delayed >24 h (vs 72%)", src: "PMID 16796010", tag: "DATA" },
    figures: [
      { t: "Mortality 72% (≤24 h) vs 87% (>24 h) to surgery", s: "PMID 16796010", tag: "DATA" },
      { t: "Delayed revascularization → 30-day mortality OR 2.09", s: "PMID 34634418", tag: "DATA" },
      { t: "Delayed surgical consultation (>24 h) → mortality aOR 9.4", s: "PMID 19350855", tag: "DATA" },
    ],
  },
  major_trauma: {
    label: "Major trauma", protocol: "Whole-body CT (pan-scan)", dose: 20, doseNote: "≈20 mSv (18–25)",
    headline: "Whole-body CT improves the probability of survival ~20–25%.",
    bar: { pct: 22.5, label: "Survival benefit of whole-body CT foregone (≈20–25%)", src: "PMID 25216568", tag: "LIT" },
    figures: [
      { t: "WBCT improves probability of survival by 20–25% vs prior methods (narrative review)", s: "PMID 25216568", tag: "LIT" },
    ],
  },
};
const ORDER = ["appendicitis", "ischemic_stroke", "pulmonary_embolism", "aortic_dissection", "mesenteric_ischemia", "subarachnoid_hemorrhage", "major_trauma"];

// --- log-scale position on the 0.001%–100% risk strip ---
const LO = Math.log10(0.001), HI = Math.log10(100);
const logPos = (pct) => Math.max(0, Math.min(1, (Math.log10(Math.max(pct, 0.001)) - LO) / (HI - LO)));

// --- count-up hook ---
function useCountUp(target, dur = 550) {
  const [v, setV] = useState(target);
  const ref = useRef(target);
  useEffect(() => {
    const from = ref.current, start = performance.now();
    let raf;
    const tick = (now) => {
      const t = Math.min(1, (now - start) / dur);
      const e = 1 - Math.pow(1 - t, 3);
      const cur = from + (target - from) * e;
      setV(cur);
      if (t < 1) raf = requestAnimationFrame(tick);
      else ref.current = target;
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [target, dur]);
  return v;
}

const fmtPct = (p) => (p >= 1 ? p.toFixed(1) : p >= 0.1 ? p.toFixed(2) : p.toFixed(3));
const fmtN = (n) => (n === Infinity ? "—" : n.toLocaleString());

export default function ComparativeRiskDashboard() {
  const [age, setAge] = useState(45);
  const [sex, setSex] = useState("F");
  const [condKey, setCondKey] = useState("pulmonary_embolism");
  const [scans, setScans] = useState(1);

  const cond = CONDS[condKey];
  const lar = computeLAR(age, sex, cond.dose, scans);
  const radPct = useCountUp(lar.pct);
  const ratio = cond.bar ? cond.bar.pct / Math.max(lar.pct, 1e-9) : null;

  const Tag = ({ k }) => (
    <span className={"tag " + (k === "DATA" ? "tag-data" : "tag-lit")}>{k}</span>
  );

  return (
    <>
      <style>{CSS}</style>
      <div className="crd">
        <header className="crd-head">
          <div className="kicker">Scenario-1 decision aid · radiation vs the risk of not scanning</div>
          <h1>When the scan itself is the smaller risk</h1>
          <p className="sub">
            Lifetime cancer risk from a CT (BEIR VII) set against the harm of withholding it for a
            time-critical diagnosis (extracted literature, Task 2). Adjust the patient and the suspected condition.
          </p>
        </header>

        {/* controls */}
        <section className="controls">
          <div className="ctrl">
            <label>Age <b>{age}</b></label>
            <input type="range" min="0" max="80" value={age} onChange={(e) => setAge(+e.target.value)} />
          </div>
          <div className="ctrl">
            <label>Sex</label>
            <div className="seg">
              {["F", "M"].map((s) => (
                <button key={s} className={sex === s ? "on" : ""} onClick={() => setSex(s)}>
                  {s === "F" ? "Female" : "Male"}
                </button>
              ))}
            </div>
          </div>
          <div className="ctrl">
            <label>Number of scans <b>{scans}</b></label>
            <div className="stepper">
              <button onClick={() => setScans(Math.max(1, scans - 1))}>–</button>
              <span>{scans}</span>
              <button onClick={() => setScans(Math.min(20, scans + 1))}>+</button>
            </div>
          </div>
          <div className="ctrl wide">
            <label>Suspected condition</label>
            <select value={condKey} onChange={(e) => setCondKey(e.target.value)}>
              {ORDER.map((k) => <option key={k} value={k}>{CONDS[k].label}</option>)}
            </select>
          </div>
        </section>

        {/* two risk panels */}
        <section className="panels">
          {/* radiation */}
          <div className="panel rad">
            <div className="panel-top">
              <span className="dot dot-rad" />
              <h2>Radiation risk of scanning</h2>
            </div>
            <div className="protocol">{cond.protocol} · {cond.doseNote}{scans > 1 ? ` × ${scans}` : ""}</div>
            <div className="bignum">
              <span className="val">{fmtPct(radPct)}<span className="unit">%</span></span>
              <span className="cap">added lifetime cancer risk</span>
            </div>
            <div className="oneinn">≈ 1 in {fmtN(lar.oneInN)} · {sex === "F" ? "female" : "male"}, age {age}</div>
            <p className="note">
              BEIR VII lifetime attributable risk (cancer incidence, all solid + leukemia),
              scaled by an effective dose of {cond.dose * scans} mSv. Point estimate with wide subjective CIs.
            </p>
          </div>

          {/* divider */}
          <div className="versus"><span>vs</span></div>

          {/* non-scanning */}
          <div className="panel harm">
            <div className="panel-top">
              <span className="dot dot-harm" />
              <h2>Risk of <i>not</i> scanning</h2>
            </div>
            <p className="headline">{cond.headline}</p>
            {cond.bar ? (
              <div className="bignum">
                <span className="val harmval">{cond.bar.pct >= 1 ? cond.bar.pct.toFixed(cond.bar.pct % 1 ? 1 : 0) : cond.bar.pct}<span className="unit">%</span></span>
                <span className="cap">{cond.bar.label} <Tag k={cond.bar.tag} /> <span className="src">{cond.bar.src}</span></span>
              </div>
            ) : (
              <div className="sparse">Insufficient primary-abstract data to quantify <Tag k="DATA" /></div>
            )}
            <ul className="figs">
              {cond.figures.map((f, i) => (
                <li key={i}><span>{f.t}</span> <Tag k={f.tag} /> <span className="src">{f.s}</span></li>
              ))}
            </ul>
          </div>
        </section>

        {/* comparison */}
        <section className="compare">
          <div className="compare-line">
            {cond.bar ? (
              <>
                For suspected <b>{cond.label.toLowerCase()}</b> in a {age}-year-old {sex === "F" ? "woman" : "man"}, the {cond.protocol.toLowerCase()} adds about{" "}
                <b className="cRad">{fmtPct(lar.pct)}%</b> lifetime cancer risk. Withholding it risks{" "}
                <b className="cHarm">{cond.bar.pct}%</b> {cond.bar.tag === "LIT" ? "(literature)" : ""} —{" "}
                roughly a <b>{ratio >= 10 ? Math.round(ratio).toLocaleString() : ratio.toFixed(1)}-fold</b> difference.
              </>
            ) : (
              <>
                For suspected <b>{cond.label.toLowerCase()}</b>, the head CT adds about{" "}
                <b className="cRad">{fmtPct(lar.pct)}%</b> lifetime cancer risk. The non-scanning harm could not be quantified
                from primary abstracts — a gap that is itself part of the manuscript's argument.
              </>
            )}
          </div>

          {/* log strip */}
          <div className="strip-wrap">
            <div className="strip">
              {[0.001, 0.01, 0.1, 1, 10, 100].map((t) => (
                <div key={t} className="tick" style={{ left: logPos(t) * 100 + "%" }}>
                  <span className="tickline" /><span className="ticklab">{t < 1 ? t : t + "%"}{t < 1 ? "%" : ""}</span>
                </div>
              ))}
              <div className="ptr ptr-rad" style={{ left: logPos(lar.pct) * 100 + "%" }} title="Radiation">
                <span className="ptr-dot" /><span className="ptr-lab">radiation {fmtPct(lar.pct)}%</span>
              </div>
              {cond.bar && (
                <div className="ptr ptr-harm" style={{ left: logPos(cond.bar.pct) * 100 + "%" }} title="Not scanning">
                  <span className="ptr-dot" /><span className="ptr-lab">not scanning {cond.bar.pct}%</span>
                </div>
              )}
            </div>
            <div className="strip-axis">probability of harm (log scale)</div>
          </div>

          <p className="kinds">
            These are different <i>kinds</i> of risk: a stochastic, lifetime cancer probability on one side; an acute, near-term
            outcome on the other. The comparison frames the trade-off — it is not a like-for-like subtraction.
          </p>
        </section>

        <footer className="crd-foot">
          <div className="src-row">
            <b>Sources</b> · Radiation: BEIR VII Phase 2, Table 12D-1 (NRC 2006); effective doses: Mettler et al., <i>Radiology</i> 2008.
            Non-scanning harm: literature extracted in Task 2 (PMIDs shown). <span className="tag tag-data">DATA</span> = extracted estimate · <span className="tag tag-lit">LIT</span> = literature constant.
          </div>
          <div className="caveat">
            Illustrative decision-framing tool. Effective dose is a population construct treated here as whole-body-equivalent for LAR;
            the linear-no-threshold model at low dose is debated; non-scanning estimates are observational and condition-specific.
            Not for individual clinical decisions.
          </div>
        </footer>
      </div>
    </>
  );
}

const CSS = `
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=IBM+Plex+Sans:wght@400;450;500;600&display=swap');
.crd{--bg:#F4F1EA;--ink:#1b1a16;--mut:#736f63;--line:#e0dbcf;--card:#fcfbf7;
 --rad:#2f7d6b;--rad-soft:#dcebe6;--harm:#b0432b;--harm-soft:#f1ddd4;
 font-family:'IBM Plex Sans',sans-serif;color:var(--ink);background:
 radial-gradient(120% 80% at 0% 0%, #f8f6f0 0%, var(--bg) 55%);
 padding:30px 26px 22px;max-width:1080px;margin:0 auto;line-height:1.5;}
.crd *{box-sizing:border-box;}
.kicker{font-size:11.5px;letter-spacing:.13em;text-transform:uppercase;color:var(--harm);font-weight:600;margin-bottom:8px;}
.crd-head h1{font-family:'Fraunces',serif;font-weight:600;font-size:35px;line-height:1.05;margin:0 0 10px;letter-spacing:-.01em;}
.sub{color:var(--mut);font-size:14.5px;max-width:640px;margin:0;}

.controls{display:grid;grid-template-columns:1.4fr .9fr .9fr 1.6fr;gap:18px;margin:26px 0 20px;
 padding:18px 20px;background:var(--card);border:1px solid var(--line);border-radius:14px;}
.ctrl{display:flex;flex-direction:column;gap:8px;min-width:0;}
.ctrl label{font-size:12px;color:var(--mut);font-weight:500;letter-spacing:.02em;}
.ctrl label b{color:var(--ink);font-weight:600;font-variant-numeric:tabular-nums;}
input[type=range]{-webkit-appearance:none;appearance:none;height:4px;border-radius:3px;background:var(--line);outline:none;}
input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:18px;height:18px;border-radius:50%;background:var(--ink);cursor:pointer;border:3px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,.2);}
input[type=range]::-moz-range-thumb{width:14px;height:14px;border-radius:50%;background:var(--ink);cursor:pointer;border:3px solid #fff;}
.seg{display:flex;border:1px solid var(--line);border-radius:9px;overflow:hidden;}
.seg button{flex:1;border:none;background:#fff;padding:8px 4px;font:inherit;font-size:13px;cursor:pointer;color:var(--mut);transition:.15s;}
.seg button.on{background:var(--ink);color:#fff;font-weight:500;}
.stepper{display:flex;align-items:center;border:1px solid var(--line);border-radius:9px;overflow:hidden;background:#fff;}
.stepper button{border:none;background:#fff;width:36px;padding:7px 0;font-size:17px;cursor:pointer;color:var(--ink);}
.stepper button:hover{background:#f0ece2;}
.stepper span{flex:1;text-align:center;font-weight:600;font-variant-numeric:tabular-nums;}
select{font:inherit;font-size:14px;padding:9px 11px;border:1px solid var(--line);border-radius:9px;background:#fff;cursor:pointer;width:100%;color:var(--ink);}

.panels{display:grid;grid-template-columns:1fr 54px 1fr;align-items:stretch;gap:0;margin-bottom:18px;}
.panel{padding:22px 24px;border-radius:14px;border:1px solid var(--line);background:var(--card);}
.panel.rad{border-top:3px solid var(--rad);}
.panel.harm{border-top:3px solid var(--harm);}
.panel-top{display:flex;align-items:center;gap:9px;margin-bottom:4px;}
.panel-top h2{font-family:'Fraunces',serif;font-weight:600;font-size:18px;margin:0;}
.panel-top h2 i{font-style:italic;}
.dot{width:9px;height:9px;border-radius:50%;display:inline-block;}
.dot-rad{background:var(--rad);}.dot-harm{background:var(--harm);}
.protocol{font-size:12.5px;color:var(--mut);margin-bottom:14px;}
.bignum{display:flex;flex-direction:column;gap:3px;margin:6px 0 8px;}
.bignum .val{font-family:'Fraunces',serif;font-weight:600;font-size:46px;line-height:1;color:var(--rad);font-variant-numeric:tabular-nums;}
.bignum .harmval{color:var(--harm);}
.bignum .unit{font-size:24px;margin-left:2px;}
.bignum .cap{font-size:12.5px;color:var(--mut);max-width:330px;}
.oneinn{font-size:14px;font-weight:500;margin-bottom:12px;}
.note{font-size:11.5px;color:var(--mut);line-height:1.45;margin:0;border-top:1px dashed var(--line);padding-top:10px;}
.headline{font-size:14.5px;font-weight:500;margin:2px 0 12px;color:#3a342b;}
.sparse{font-size:14px;color:var(--harm);font-weight:500;margin:8px 0 12px;}
.figs{list-style:none;padding:0;margin:8px 0 0;border-top:1px dashed var(--line);padding-top:12px;display:flex;flex-direction:column;gap:9px;}
.figs li{font-size:12.5px;line-height:1.4;}
.src{color:var(--mut);font-size:11px;}
.versus{display:flex;align-items:center;justify-content:center;}
.versus span{font-family:'Fraunces',serif;font-style:italic;font-size:17px;color:var(--mut);background:var(--bg);width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;border:1px solid var(--line);}

.tag{font-size:9px;font-weight:700;letter-spacing:.06em;padding:1.5px 5px;border-radius:5px;vertical-align:middle;}
.tag-data{background:var(--rad-soft);color:var(--rad);}
.tag-lit{background:#efe7d4;color:#8a6d22;}

.compare{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:22px 26px 18px;margin-bottom:16px;}
.compare-line{font-size:16px;line-height:1.55;margin-bottom:26px;}
.compare-line b{font-weight:600;}
.cRad{color:var(--rad);}.cHarm{color:var(--harm);}
.strip-wrap{margin:8px 4px 4px;}
.strip{position:relative;height:74px;border-bottom:2px solid var(--line);margin-bottom:6px;}
.tick{position:absolute;bottom:0;transform:translateX(-50%);text-align:center;}
.tickline{display:block;width:1px;height:7px;background:var(--line);margin:0 auto;}
.ticklab{font-size:10px;color:var(--mut);font-variant-numeric:tabular-nums;}
.ptr{position:absolute;bottom:9px;transform:translateX(-50%);transition:left .5s cubic-bezier(.22,1,.36,1);text-align:center;}
.ptr-dot{display:block;width:14px;height:14px;border-radius:50%;margin:0 auto 3px;border:2.5px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,.18);}
.ptr-rad{z-index:2;} .ptr-rad .ptr-dot{background:var(--rad);}
.ptr-harm{z-index:3;} .ptr-harm .ptr-dot{background:var(--harm);}
.ptr-lab{font-size:11px;font-weight:600;white-space:nowrap;}
.ptr-rad .ptr-lab{color:var(--rad);} .ptr-harm .ptr-lab{color:var(--harm);}
.ptr-rad{bottom:34px;} .ptr-harm{bottom:9px;}
.strip-axis{font-size:10.5px;color:var(--mut);text-align:center;letter-spacing:.04em;}
.kinds{font-size:12.5px;color:var(--mut);line-height:1.5;margin:20px 0 0;border-top:1px dashed var(--line);padding-top:14px;}
.kinds i{font-style:italic;}

.crd-foot{font-size:11px;color:var(--mut);line-height:1.5;display:flex;flex-direction:column;gap:8px;}
.crd-foot b{color:#4a463c;}
.caveat{font-style:italic;}

@media(max-width:760px){
 .controls{grid-template-columns:1fr 1fr;}
 .panels{grid-template-columns:1fr;gap:14px;}
 .versus{display:none;}
 .crd-head h1{font-size:27px;}
 .bignum .val{font-size:38px;}
}
`;
