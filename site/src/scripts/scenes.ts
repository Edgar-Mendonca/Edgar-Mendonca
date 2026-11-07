// The two animated drawings in the Tools section: the SHPB firing, and CentriForge's compressor train running
// against its performance map. Each loops while on screen and pauses off screen; with "reduce motion" set they
// stay as finished drawings.
import gsap from "gsap";

type Build = (root: Element) => gsap.core.Timeline;
const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
const finder = (root: Element) => <T extends Element = SVGElement>(id: string) => root.querySelector<T>(`#${id}`)!;
const say = (el: Element | null, text: string) => () => { if (el) el.textContent = text; };

// Split Hopkinson Pressure Bar: striker, incident pulse, reflection and transmission, three traces.
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
    .to(q("sc-cursor"), { opacity: 0, duration: 0.3 }, "hit+=2.4")
    .to({}, { duration: 1.6 });
  return tl;
};

// CentriForge: the train spins up with the map's speed; the operating point climbs to full speed, drifts towards
// surge, the anti-surge valve opens, and the point recovers.
const centriforge: Build = root => {
  const q = finder(root);
  const path = q<SVGPathElement>("cf-run"), dot = q("cf-dot"), len = path.getTotalLength();
  const b1 = Number(path.dataset.b1), b2 = Number(path.dataset.b2);
  const speedT = q("cf-speed"), state = q("cf-state"), asv = q("cf-asv");
  const rotD = q("cf-rotD"), rotC = q("cf-rotC");
  const wheel = root.querySelector<SVGGElement>(".cf-wheel"), pinion = root.querySelector<SVGGElement>(".cf-pinion");
  const at = { p: 0 };
  let phiD = 0, phiC = 0;
  const speed = () => Math.min(1, at.p / b1);
  const draw = () => {
    const pt = path.getPointAtLength(at.p * len);
    dot.setAttribute("cx", pt.x.toFixed(1)); dot.setAttribute("cy", pt.y.toFixed(1));
    path.style.strokeDashoffset = String(1000 * (1 - at.p));
    speedT.textContent = `SPEED ${Math.round(speed() * 100)} %`;
  };
  // Shafts, couplings and gears turn at a rate set by the speed: driver side slow, compressor side ~2.5× faster.
  const spin = (_t: number, dt: number) => {
    const s = speed(); phiD += (dt / 1000) * s * 1.1; phiC = phiD * 2.47;
    rotD?.setAttribute("patternTransform", `translate(0 ${((phiD * 56) % 60).toFixed(2)})`);
    rotC?.setAttribute("patternTransform", `translate(0 ${((phiC * 56) % 60).toFixed(2)})`);
    wheel?.setAttribute("transform", `rotate(${((phiD * 360) % 360).toFixed(1)} ${wheel.dataset.c})`);
    pinion?.setAttribute("transform", `rotate(${(-(phiC * 360) % 360).toFixed(1)} ${pinion.dataset.c})`);
    root.style.setProperty("--flow", String(s));
  };
  const tl = gsap.timeline({ defaults: { ease: "none" } });
  gsap.ticker.add((t, dt) => { if (!tl.paused()) spin(t, dt); });   // registered once; idle while paused off screen
  tl.set(path, { strokeDasharray: 1000 })
    .call(() => { at.p = 0; draw(); asv.textContent = "ANTI-SURGE VALVE CLOSED"; asv.classList.remove("open"); })
    .call(say(state, "STARTING"))
    .to(at, { p: b1, duration: 2.6, ease: "power1.inOut", onUpdate: draw })
    .call(say(state, "FULL SPEED"))
    .to(at, { p: b2, duration: 2.2, ease: "power1.in", onUpdate: draw }, "+=0.3")
    .call(say(state, "NEAR SURGE"))
    .call(() => { asv.textContent = "ANTI-SURGE VALVE OPEN"; asv.classList.add("open"); }, [], "+=0.2")
    .call(say(state, "RECYCLING"))
    .to(at, { p: 1, duration: 1.5, ease: "power2.out", onUpdate: draw }, "+=0.2")
    .call(say(state, "STABLE"))
    .to({}, { duration: 2.0 });
  return tl;
};

const builders: Record<string, Build> = { shpb, centriforge };

export function setupScenes() {
  if (reduce) return;
  document.querySelectorAll<HTMLElement | SVGElement>("[data-scene]").forEach(el => {
    const build = builders[el.dataset.scene ?? ""];
    if (!build) return;
    const tl = build(el).repeat(-1).pause();
    new IntersectionObserver(([e]) => {
      el.classList.toggle("run", e.isIntersecting);
      if (e.isIntersecting) tl.play(); else tl.pause();
    }, { threshold: 0.25 }).observe(el);
  });
}
