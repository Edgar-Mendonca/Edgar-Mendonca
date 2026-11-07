// The hero bench: four animated scenes from the work. Each builder returns a GSAP timeline that plays the scene
// once from its starting state; the controller plays them in turn and the tabs switch between them.
// With "reduce motion" set, the tabs still switch but every scene shows its finished drawing.
import gsap from "gsap";

type Build = (svg: SVGSVGElement) => gsap.core.Timeline;
const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;

const finder = (svg: SVGSVGElement) => <T extends Element = SVGElement>(id: string) => svg.querySelector<T>(`#${id}`)!;
const say = (el: Element | null, text: string) => () => { if (el) el.textContent = text; };

// 1. Split Hopkinson Pressure Bar: striker, incident pulse, reflection and transmission, three traces.
const shpb: Build = svg => {
  const q = finder(svg);
  const traces = ["sc-ti", "sc-tr", "sc-tt"].map(id => q(id));
  const tl = gsap.timeline({ defaults: { ease: "none" } });
  tl.call(say(q("sc-state"), "FIRING"))
    .set([q("sc-pi"), q("sc-pr"), q("sc-pt")], { opacity: 0 })
    .set(traces, { strokeDasharray: 1000, strokeDashoffset: 1000 })
    .set(q("sc-cursor"), { opacity: 0, x: 0 })
    .set(q("sc-striker"), { x: 0 })
    .fromTo(q("sc-v"), { autoAlpha: 0, x: -6 }, { autoAlpha: 1, x: 0, duration: 0.3, ease: "power2.out" })
    .to(q("sc-striker"), { x: 26, duration: 0.55, ease: "power2.in" }, "<")
    .to(q("sc-v"), { autoAlpha: 0, duration: 0.2 })
    .addLabel("hit")
    .set(q("sc-pi"), { opacity: 1, x: 0 }, "hit")
    .to(q("sc-cursor"), { opacity: 0.5, duration: 0.1 }, "hit")
    .to(q("sc-cursor"), { x: 500, duration: 2.4 }, "hit")
    .to(q("sc-pi"), { x: 230, duration: 1.0 }, "hit")
    .to(traces, { strokeDashoffset: 0, duration: 2.4 }, "hit")
    .call(() => q("sc-g1").classList.add("hot"), [], "hit+=0.48").call(() => q("sc-g1").classList.remove("hot"), [], "hit+=0.75")
    .to(q("sc-spec"), { scaleX: 0.72, transformOrigin: "50% 50%", duration: 0.18, yoyo: true, repeat: 1, ease: "power1.inOut" }, "hit+=0.95")
    .to(q("sc-pi"), { opacity: 0, duration: 0.15 }, "hit+=0.95")
    .set(q("sc-pr"), { opacity: 1, x: 0 }, "hit+=1.0")
    .to(q("sc-pr"), { x: -230, duration: 1.0 }, "hit+=1.0")
    .set(q("sc-pt"), { opacity: 0.9, x: 0 }, "hit+=1.0")
    .to(q("sc-pt"), { x: 260, duration: 1.1 }, "hit+=1.0")
    .call(() => q("sc-g2").classList.add("hot"), [], "hit+=1.45").call(() => q("sc-g2").classList.remove("hot"), [], "hit+=1.75")
    .to(q("sc-striker"), { x: 0, duration: 0.6, ease: "power2.inOut" }, "hit+=1.2")
    .to([q("sc-pr"), q("sc-pt")], { opacity: 0, duration: 0.2 }, "hit+=2.1")
    .call(say(q("sc-state"), "RECORDED"), [], "hit+=2.4")
    .to(q("sc-cursor"), { opacity: 0, duration: 0.3 }, "hit+=2.4");
  return tl;
};

// 2. API 617 train: start-up along the system curve, drift towards surge, anti-surge valve opens, back to safety.
const train: Build = svg => {
  const q = finder(svg);
  const path = q<SVGPathElement>("c-run"), dot = q("c-dot"), len = path.getTotalLength();
  const b1 = Number(path.dataset.b1), b2 = Number(path.dataset.b2);
  const speed = q("c-speed"), state = q("c-state"), valve = q("c-asv").querySelector("path")!, vt = q("c-asv-t"), rflow = q("c-rflow");
  const at = { p: 0 };
  const draw = () => {
    const pt = path.getPointAtLength(at.p * len);
    dot.setAttribute("cx", pt.x.toFixed(1)); dot.setAttribute("cy", pt.y.toFixed(1));
    path.style.strokeDashoffset = String(1000 * (1 - at.p));
    speed.textContent = `N ${Math.round(Math.min(1, at.p / b1) * 100)} %`;
  };
  const tl = gsap.timeline({ defaults: { ease: "none" } });
  tl.set(path, { strokeDasharray: 1000 })
    .call(() => { at.p = 0; draw(); valve.classList.remove("open"); vt.textContent = "ASV CLOSED"; gsap.set(rflow, { opacity: 0 }); })
    .call(say(state, "STARTING"))
    .to(at, { p: b1, duration: 2.2, ease: "power1.inOut", onUpdate: draw })
    .call(say(state, "FULL SPEED"))
    .to(at, { p: b2, duration: 2.0, ease: "power1.in", onUpdate: draw }, "+=0.2")
    .call(say(state, "NEAR SURGE"))
    .call(() => { valve.classList.add("open"); vt.textContent = "ASV OPEN"; }, [], "+=0.15")
    .to(rflow, { opacity: 0.85, duration: 0.3 }, "<")
    .call(say(state, "RECYCLING"))
    .to(at, { p: 1, duration: 1.4, ease: "power2.out", onUpdate: draw }, "+=0.2")
    .call(say(state, "STABLE"))
    .to({}, { duration: 0.6 });
  return tl;
};

// 3. Stress waves: ball strikes a free bar, compression out, tension back, axial and lateral traces.
const waves: Build = svg => {
  const q = finder(svg);
  const traces = [q("w-ax"), q("w-lat")];
  const tl = gsap.timeline({ defaults: { ease: "none" } });
  tl.set(traces, { strokeDasharray: 1000, strokeDashoffset: 1000 })
    .set([q("w-pc"), q("w-pt")], { opacity: 0, x: 0 })
    .set(q("w-cursor"), { opacity: 0, x: 0 })
    .fromTo(q("w-pend"), { rotate: 48 }, { rotate: 0, duration: 0.8, ease: "power2.in" })
    .addLabel("hit")
    .to(q("w-pend"), { rotate: 9, duration: 0.5, ease: "power2.out", yoyo: true, repeat: 1 }, "hit")
    .set(q("w-pc"), { opacity: 1 }, "hit")
    .to(q("w-pc"), { x: 470, duration: 1.0 }, "hit")
    .to(q("w-cursor"), { opacity: 0.5, duration: 0.1 }, "hit")
    .to(q("w-cursor"), { x: 500, duration: 2.6 }, "hit")
    .to(traces, { strokeDashoffset: 0, duration: 2.6 }, "hit")
    .call(() => q("w-g").classList.add("hot"), [], "hit+=0.47").call(() => q("w-g").classList.remove("hot"), [], "hit+=0.72")
    .to(q("w-pc"), { opacity: 0, duration: 0.12 }, "hit+=0.95")
    .set(q("w-pt"), { opacity: 1 }, "hit+=1.0")
    .to(q("w-pt"), { x: -438, duration: 1.0 }, "hit+=1.0")
    .call(() => q("w-g").classList.add("hot"), [], "hit+=1.48").call(() => q("w-g").classList.remove("hot"), [], "hit+=1.73")
    .to(q("w-pt"), { opacity: 0, duration: 0.15 }, "hit+=1.9")
    .to(q("w-cursor"), { opacity: 0, duration: 0.3 }, "hit+=2.6");
  return tl;
};

// 4. Ring compression: the plate comes down, the ring flattens, the load–deflection curve is drawn.
const ring: Build = svg => {
  const q = finder(svg);
  const path = q<SVGPathElement>("r-curve"), dot = q("r-dot"), top = q("r-top"), ell = q("r-ring"), dl = q("r-d"), len = path.getTotalLength();
  const at = { p: 0 };
  const draw = () => {
    const p = at.p, ry = 22 - 10 * p, rx = 22 + 8 * p;
    top.setAttribute("transform", `translate(0 ${(20 * p).toFixed(2)})`);
    ell.setAttribute("rx", rx.toFixed(2)); ell.setAttribute("ry", ry.toFixed(2)); ell.setAttribute("cy", (108 - ry).toFixed(2));
    const pt = path.getPointAtLength(p * len);
    dot.setAttribute("cx", pt.x.toFixed(1)); dot.setAttribute("cy", pt.y.toFixed(1));
    path.style.strokeDashoffset = String(1000 * (1 - p));
    dl.textContent = `δ / R = ${(0.91 * p).toFixed(2)}`;
  };
  const tl = gsap.timeline({ defaults: { ease: "none" } });
  tl.set(path, { strokeDasharray: 1000 })
    .call(() => { at.p = 0; draw(); })
    .to(at, { p: 1, duration: 3.6, ease: "power1.inOut", onUpdate: draw }, "+=0.3")
    .to({}, { duration: 0.8 });
  return tl;
};

const builders: Record<string, Build> = { shpb, train, waves, ring };

export function setupBench() {
  const root = document.querySelector<HTMLElement>("[data-bench]");
  if (!root) return;
  const tabs = [...root.querySelectorAll<HTMLButtonElement>("[role=tab]")];
  const panels = [...root.querySelectorAll<HTMLElement>(".bpanel")];
  let cur = 0, tl: gsap.core.Timeline | null = null, timer = 0, visible = true, first = true;

  const show = (k: number, focus = false) => {
    cur = (k + tabs.length) % tabs.length;
    tabs.forEach((t, j) => { t.setAttribute("aria-selected", String(j === cur)); t.tabIndex = j === cur ? 0 : -1; t.style.setProperty("--p", "0"); });
    panels.forEach((p, j) => { p.hidden = j !== cur; });
    if (focus) tabs[cur].focus();
    clearTimeout(timer); tl?.kill(); tl = null;
    root.querySelectorAll("svg.scene").forEach(s => s.classList.remove("run"));
    const svg = panels[cur].querySelector<SVGSVGElement>("svg.scene");
    if (reduce || !svg) return;
    svg.classList.add("run");
    const t = (tl = builders[svg.dataset.scene ?? ""]?.(svg) ?? null);
    if (!t) return;
    t.delay(first ? 0.9 : 0.25); first = false;
    t.eventCallback("onUpdate", () => tabs[cur].style.setProperty("--p", t.progress().toFixed(3)));
    t.eventCallback("onComplete", () => { tabs[cur].style.setProperty("--p", "1"); timer = window.setTimeout(() => show(cur + 1), 1800); });
    if (!visible) t.pause();
  };

  tabs.forEach((t, k) => t.addEventListener("click", () => show(k)));
  root.querySelector("[role=tablist]")?.addEventListener("keydown", e => {
    const key = (e as KeyboardEvent).key;
    if (key === "ArrowRight" || key === "ArrowLeft") { e.preventDefault(); show(cur + (key === "ArrowRight" ? 1 : -1), true); }
    if (key === "Home" || key === "End") { e.preventDefault(); show(key === "Home" ? 0 : tabs.length - 1, true); }
  });
  // Pause the bench while it is off screen.
  new IntersectionObserver(([e]) => {
    visible = e.isIntersecting;
    if (!tl) return;
    if (visible) { tl.resume(); if (tl.progress() === 1) show(cur + 1); } else tl.pause();
  }).observe(root);

  show(0);
}
