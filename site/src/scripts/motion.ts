// Motion for the whole site: smooth scrolling (Lenis), scroll reveals and the hero's Hopkinson bar (GSAP).
// Everything is visible without this script; with "reduce motion" set, only the reading-progress line runs.
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import Lenis from "lenis";

gsap.registerPlugin(ScrollTrigger);
const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
const $$ = <T extends Element = HTMLElement>(s: string, r: ParentNode = document) => [...r.querySelectorAll<T>(s)];

// ---------- reading progress: an amber line under the header ----------
const bar = document.querySelector<HTMLElement>(".progress");
if (bar) {
  const set = () => {
    const max = document.documentElement.scrollHeight - innerHeight;
    bar.style.transform = `scaleX(${max > 0 ? Math.min(1, scrollY / max) : 0})`;
  };
  addEventListener("scroll", set, { passive: true });
  addEventListener("resize", set);
  set();
}

// ---------- small drawings run only while on screen ----------
const io = new IntersectionObserver(es => es.forEach(e => e.target.classList.toggle("on", e.isIntersecting)), { rootMargin: "60px" });
$$(".glyph").forEach(g => io.observe(g));

if (!reduce) {
  document.documentElement.classList.add("motion");

  // ---------- smooth scroll ----------
  const lenis = new Lenis({ duration: 1.1, easing: t => 1 - Math.pow(1 - t, 3), anchors: false });
  lenis.on("scroll", ScrollTrigger.update);
  gsap.ticker.add(t => lenis.raf(t * 1000));
  gsap.ticker.lagSmoothing(0);
  // Where an anchor should land: a section bar sits right under the header; anything else also clears the bar.
  const head = () => document.querySelector<HTMLElement>(".site-head")?.offsetHeight ?? 60;
  const target = (el: HTMLElement) => {
    // Sticky bars report their stuck position, so measure from the document, not the viewport.
    let y = 0; for (let n: HTMLElement | null = el; n; n = n.offsetParent as HTMLElement | null) y += n.offsetTop;
    return Math.max(0, y - head() - (el.classList.contains("bar") ? 0 : 44));
  };
  document.addEventListener("click", e => {
    const a = (e.target as HTMLElement).closest<HTMLAnchorElement>("a[href*='#']");
    if (!a || e.defaultPrevented || e.metaKey || e.ctrlKey) return;
    const url = new URL(a.href, location.href);
    if (url.pathname.replace(/\/$/, "") !== location.pathname.replace(/\/$/, "") || !url.hash) return;
    const el = document.getElementById(decodeURIComponent(url.hash.slice(1)));
    if (!el) return;
    e.preventDefault();
    lenis.scrollTo(target(el));
    history.replaceState(null, "", url.hash);
  });
  if (location.hash) {
    const el = document.getElementById(decodeURIComponent(location.hash.slice(1)));
    if (el) requestAnimationFrame(() => lenis.scrollTo(target(el), { immediate: true }));
  }

  // ---------- headings come in word by word ----------
  const split = (el: HTMLElement) => {
    const walk = (n: Node) => {
      for (const c of [...n.childNodes]) {
        if (c.nodeType === 3) {
          const frag = document.createDocumentFragment();
          for (const part of (c.textContent ?? "").split(/(\s+)/)) {
            if (!part) continue;
            if (/^\s+$/.test(part)) { frag.append(part); continue; }
            const w = document.createElement("span"); w.className = "w";
            const i = document.createElement("span"); i.className = "wi"; i.textContent = part;
            w.append(i); frag.append(w);
          }
          c.replaceWith(frag);
        } else if (c.nodeType === 1 && !(c as HTMLElement).classList.contains("w")) {
          const el2 = c as HTMLElement;
          if (el2.classList.contains("it")) {      // keep the italic accent as one piece
            const w = document.createElement("span"); w.className = "w";
            el2.replaceWith(w); el2.classList.add("wi"); w.append(el2);
          } else walk(c);
        }
      }
    };
    walk(el);
    return $$(".wi", el);
  };

  // ---------- hero: name, line, buttons, then the facts ----------
  const hero = document.querySelector(".hero");
  if (hero) {
    const tl = gsap.timeline({ defaults: { ease: "power3.out" } });
    const name = hero.querySelector<HTMLElement>("h1");
    if (name) tl.from(split(name), { yPercent: 110, duration: 0.9, stagger: 0.08 }, 0.1);
    tl.from($$(".hero .mono.muted, .hero .lead, .hero .btns", hero), { y: 18, autoAlpha: 0, duration: 0.7, stagger: 0.1 }, 0.25)
      .from($$(".facts > div", hero), { y: 14, autoAlpha: 0, duration: 0.6, stagger: 0.08 }, 0.6);
  }

  // ---------- section headings ----------
  $$(".h2, .article h2").forEach(h => {
    const words = split(h);
    gsap.from(words, { yPercent: 110, duration: 0.8, ease: "power3.out", stagger: 0.06, scrollTrigger: { trigger: h, start: "top 88%" } });
  });

  // ---------- cards, boxes and figures rise in, in groups ----------
  const rising = $$(".reveal, .fig, .lead:not(.hero .lead)");
  if (rising.length) {
    gsap.set(rising, { y: 26, autoAlpha: 0 });
    ScrollTrigger.batch(rising, {
      start: "top 90%",
      onEnter: els => gsap.to(els, { y: 0, autoAlpha: 1, duration: 0.8, ease: "power3.out", stagger: 0.08, overwrite: true }),
    });
  }
  const icons = $$(".app img");
  if (icons.length) ScrollTrigger.batch(icons, {
    start: "top 92%",
    onEnter: els => gsap.from(els, { scale: 0.6, rotate: -10, autoAlpha: 0, duration: 0.7, ease: "back.out(1.8)", stagger: 0.06 }),
  });

  // ---------- section bars: the number slides in, the rule draws ----------
  $$(".bar").forEach(b => {
    gsap.from(b.querySelectorAll("span"), { x: -14, autoAlpha: 0, duration: 0.6, ease: "power2.out", stagger: 0.1, scrollTrigger: { trigger: b, start: "top 92%" } });
  });

  // ---------- screenshots drift a little against the scroll ----------
  $$(".feature .pic img").forEach(img => {
    gsap.fromTo(img, { y: 18 }, { y: -18, ease: "none", scrollTrigger: { trigger: img, start: "top bottom", end: "bottom top", scrub: true } });
  });

  // ---------- the Hopkinson bar ----------
  const scene = document.querySelector<SVGSVGElement>(".scene");
  if (scene) {
    const q = (id: string) => scene.querySelector(`#${id}`);
    const traces = ["sc-ti", "sc-tr", "sc-tt"].map(q);
    const state = q("sc-state");
    gsap.set(traces, { strokeDasharray: 1000, strokeDashoffset: 1000 });   // traces have pathLength 1000
    const tl = gsap.timeline({ repeat: -1, repeatDelay: 1.4, delay: 0.8, defaults: { ease: "none" } });
    tl.call(() => { if (state) state.textContent = "FIRING"; });
    tl.set(["#sc-pi", "#sc-pr", "#sc-pt"].map(s => scene.querySelector(s)), { opacity: 0 })
      .set(traces, { strokeDashoffset: 1000 })
      .set(q("sc-cursor"), { opacity: 0, x: 0 })
      .fromTo(q("sc-v"), { autoAlpha: 0, x: -6 }, { autoAlpha: 1, x: 0, duration: 0.3, ease: "power2.out" })
      // striker accelerates down the barrel and hits the bar
      .fromTo(q("sc-striker"), { x: 0 }, { x: 26, duration: 0.55, ease: "power2.in" }, "<")
      .to(q("sc-v"), { autoAlpha: 0, duration: 0.2 })
      // incident pulse to the specimen; the scope cursor sweeps with time
      .set(q("sc-pi"), { opacity: 1, x: 0 }, "hit")
      .to(q("sc-cursor"), { opacity: 0.5, duration: 0.1 }, "hit")
      .to(q("sc-cursor"), { x: 500, duration: 2.4 }, "hit")
      .to(q("sc-pi"), { x: 230, duration: 1.0 }, "hit")
      .to(q("sc-ti"), { strokeDashoffset: 0, duration: 2.4 }, "hit")
      .call(() => q("sc-g1")?.classList.add("hot"), [], "hit+=0.48").call(() => q("sc-g1")?.classList.remove("hot"), [], "hit+=0.75")
      // at the specimen: it squeezes, part of the pulse reflects and part passes on
      .to(q("sc-spec"), { scaleX: 0.72, transformOrigin: "50% 50%", duration: 0.18, yoyo: true, repeat: 1, ease: "power1.inOut" }, "hit+=0.95")
      .to(q("sc-pi"), { opacity: 0, duration: 0.15 }, "hit+=0.95")
      .set(q("sc-pr"), { opacity: 1, x: 0 }, "hit+=1.0")
      .to(q("sc-pr"), { x: -230, duration: 1.0 }, "hit+=1.0")
      .set(q("sc-pt"), { opacity: 0.9, x: 0 }, "hit+=1.0")
      .to(q("sc-pt"), { x: 260, duration: 1.1 }, "hit+=1.0")
      .call(() => q("sc-g2")?.classList.add("hot"), [], "hit+=1.45").call(() => q("sc-g2")?.classList.remove("hot"), [], "hit+=1.75")
      .to(q("sc-tr"), { strokeDashoffset: 0, duration: 2.4 }, "hit")
      .to(q("sc-tt"), { strokeDashoffset: 0, duration: 2.4 }, "hit")
      .to(q("sc-striker"), { x: 0, duration: 0.6, ease: "power2.inOut" }, "hit+=1.2")
      .call(() => { if (state) state.textContent = "RECORDED"; }, [], "hit+=2.4")
      .to(q("sc-cursor"), { opacity: 0, duration: 0.3 }, "hit+=2.4")
      .to([q("sc-pr"), q("sc-pt")], { opacity: 0, duration: 0.2 }, "hit+=2.1");
    // pause while off screen
    ScrollTrigger.create({ trigger: scene, start: "top bottom", end: "bottom top", onToggle: s => (s.isActive ? tl.play() : tl.pause()) });
  }
}
