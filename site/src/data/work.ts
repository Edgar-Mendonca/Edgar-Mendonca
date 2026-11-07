// Everything the home page lists, in one place. Edit here; the pages read it.
const gh = "https://github.com/Edgar-Mendonca";

export const person = {
  name: "Edgar Mendonca",
  role: "Engineer, researcher, developer",
  github: gh,
  linkedin: "https://www.linkedin.com/in/edgar-mendonca/",
  youtube: "https://www.youtube.com/@edgarmendonca",
};

/** The Datum family: free, open-source desktop apps (Rust, Tauri 2, SolidJS). */
export const datum = {
  site: "https://edgar-mendonca.github.io/Datum/",
  repo: `${gh}/Datum`,
  apps: [
    { id: "plan", name: "Datum Plan", line: "Plan, schedule, track and report projects.", version: "0.6.0" },
    { id: "plot", name: "Datum Plot", line: "Analyse data and make publication-ready graphs.", version: "0.3.19" },
    { id: "atlas", name: "Datum Atlas", line: "Choose materials with property charts and selection indices.", version: "0.3.0" },
    { id: "sim", name: "Datum Sim", line: "Model and simulate dynamic systems: block diagrams, control and motors.", version: "0.2.1" },
    { id: "calc", name: "Datum Calc", line: "Engineering calculations with real units, checks and a printable calc sheet.", version: "0.1.11" },
    { id: "mesh", name: "Datum Mesh", line: "Finite-element analysis: stresses, deflections and temperatures in parts and frames.", version: "0.9.1" },
    { id: "pipe", name: "Datum Pipe", line: "Pipe stress analysis with code stresses, nozzle loads and an automatic isometric.", version: "0.6.0" },
    { id: "schema", name: "Datum Schema", line: "Intelligent P&IDs and process flow diagrams: draw, check and list.", version: "0.7.5" },
    { id: "layout", name: "Datum Layout", line: "3D plant layout and piping: place equipment, route lines, check clashes.", version: "0.1.4" },
  ].map(a => ({
    ...a,
    icon: `icons/datum-${a.id}-icon.svg`,
    page: `https://edgar-mendonca.github.io/Datum/apps/${a.id}`,
    repo: `${gh}/Datum-${a.id[0].toUpperCase()}${a.id.slice(1)}`,
  })),
};

export const centriforge = {
  name: "CentriForge",
  line: "Compressor engineering suite for industrial centrifugal compressors (API 617 scope).",
  version: "0.5.7",
  repo: `${gh}/Compressor-Engineering-Suite`,
  download: `${gh}/Compressor-Engineering-Suite/releases/latest`,
  icon: "icons/centriforge.svg",
  about:
    "Preliminary design, selection, simulation and technical evaluation of centrifugal compressors in one desktop app. Every module works on one shared engineering model, so a change to the gas, an operating case, the shaft or a bearing runs through thermodynamics, aerodynamics, rotordynamics and verification in a single pass.",
  points: [
    "Real-gas thermodynamics, polytropic compression and stage-stacked performance maps with surge and stonewall",
    "Impeller and rotor mechanics with 3D cyclic-sector FEA, bearings, seals and lateral and torsional rotordynamics",
    "Anti-surge dynamics, shop-test planning to ASME PTC 10 and a checklist of every module's checks",
    "Datasheets and calculation reports; Windows installer with one-click updates (Python engine, React UI)",
  ],
  tags: ["Python", "FastAPI", "React", "TypeScript", "API 617"],
};

export const shpbTool = {
  name: "SHPB Analysis Tool",
  line: "Turns raw Split Hopkinson Pressure Bar signals into strain-rate, stress–strain and true stress–strain curves.",
  icon: "icons/shpb.svg",
  python: `${gh}/SHPB-Analysis`,
  matlab: `${gh}/Split-Hopkinson-Pressure-Bar-Analysis-Tool`,
  video: "https://www.youtube.com/watch?v=0fWdUWLbv9A",
};

export const engineering = [
  {
    title: "Export Gas Compressor Package (API 617)",
    when: "Jul 2024 – present",
    where: "EPC / manufacturing · Oil and gas",
    img: "img/work/compressor-package.png",
    text:
      "Supply and engineering of the export gas compressor package for the Sahil Phase 3 Development Project. Design review, compliance and technical coordination with the compressor manufacturer (SBW) against ADNOC specifications.",
    points: [
      "Interface with sub-vendors: ABB (motor, VFD, GIS), Burgmann (dry gas seals, seal gas boosters), Kelvion (heat exchangers), Hitachi (VFD transformer), Rittal (VFD chiller) and Flender (gearbox)",
      "Specification compliance and integration of every sub-system into one package",
    ],
    tags: ["API 617", "EPC", "Rotating equipment", "Vendor management"],
  },
];

/** Research topics, shown as simple boxes. `links` go to a case study on this site, a PDF or code. */
export const research = [
  {
    kind: "Experimental rig",
    title: "Split Hopkinson Pressure Bar", glyph: "shpb" as const,
    when: "Nov 2018 – Apr 2021",
    text: "Designed and built a bar for testing materials at strain rates of 10² to 10⁴ s⁻¹: the frame, gas gun, velocity gate, strain-gauge amplifiers and the analysis code.",
    links: [{ label: "Read the study", page: "research/shpb" }, { label: "Analysis code", href: `${gh}/SHPB-Analysis` }],
  },
  {
    kind: "Experiment and theory",
    title: "Stress waves in solids", glyph: "waves" as const,
    when: "2019",
    text: "Ball-on-bar and bar-on-bar impacts: how stress pulses travel, reflect and change at a step, and Young's modulus and Poisson's ratio measured from them.",
    links: [{ label: "Read the study", page: "research/stress-waves" }, { label: "Paper (PDF)", href: "https://drive.google.com/file/d/11_lwCQQhr5Gb55sdCd_Ul4YJYndI3UiR/view" }],
  },
  {
    kind: "Bachelor's thesis · papers",
    title: "Axial crushing of metal tubes", glyph: "axial" as const,
    when: "",
    text: "How metal tubes deform and absorb impact energy under axial compression, and how strain hardening changes the plastic buckling of aluminium tubes.",
    links: [
      { label: "Thesis (PDF)", href: "https://drive.google.com/file/d/150Ns480wjIrKlEM9jr_URIjchdEYe8oc/view" },
      { label: "Paper 1 (PDF)", href: "https://drive.google.com/file/d/1oM4l2MszLuWkSD3mIIxX7GT8uPtWoWp-/view" },
      { label: "Paper 2 (PDF)", href: "https://drive.google.com/file/d/1fxbm2O-PM-BKtYirUnGmKk84FdBJ36Up/view" },
    ],
  },
  {
    kind: "Experiment and theory",
    title: "Lateral compression of tubes", glyph: "lateral" as const,
    when: "Mar 2022 – May 2023",
    text: "Aluminium 6063 rings crushed between flat plates: yield stress, elastic modulus and hardening modulus from one load–deflection curve, checked against theory.",
    links: [{ label: "Read the study", page: "research/lateral-compression" }, { label: "Code", href: `${gh}/Load-deflection-characteristics-of-lateral-compression-of-tubes` }],
  },
  {
    kind: "Master's thesis",
    title: "Slip activity in nickel alloys", glyph: "grains" as const,
    when: "",
    text: "How prior deformation changes slip in nickel alloys, mapped grain by grain with high-resolution digital image correlation (HRDIC) and EBSD.",
    links: [{ label: "Thesis (PDF)", href: "https://drive.google.com/file/d/1ak9HJxILX0hKhumFyu9-c-gX-TRa86Na/view" }],
  },
];

export const papers = [
  {
    title: "Effect of prior deformation on slip activity in nickel alloys",
    note: "Master's thesis · slip, grain orientation and microstructure from HRDIC and EBSD maps",
    href: "https://drive.google.com/file/d/1ak9HJxILX0hKhumFyu9-c-gX-TRa86Na/view",
  },
  {
    title: "Studies on deformation behaviour and impact energy absorption of metal tubes under axial compression",
    note: "Bachelor's thesis",
    href: "https://drive.google.com/file/d/150Ns480wjIrKlEM9jr_URIjchdEYe8oc/view",
  },
  {
    title: "Effects of strain-hardening during plastic buckling for axially compressed aluminium tubes",
    note: "Paper",
    href: "https://drive.google.com/file/d/1oM4l2MszLuWkSD3mIIxX7GT8uPtWoWp-/view",
  },
  {
    title: "Strain-hardening effects during plastic buckling of axially compressed aluminium tubes",
    note: "Paper",
    href: "https://drive.google.com/file/d/1fxbm2O-PM-BKtYirUnGmKk84FdBJ36Up/view",
  },
  {
    title: "Elementary experimental studies on stress wave propagation in bars",
    note: "Paper · E. V. Mendonca, P. B. Shahapur, T. Y. Reddy (2019)",
    href: "https://drive.google.com/file/d/11_lwCQQhr5Gb55sdCd_Ul4YJYndI3UiR/view",
  },
];

export const code = [
  { title: "Load–deflection of tubes in lateral compression", href: `${gh}/Load-deflection-characteristics-of-lateral-compression-of-tubes` },
  { title: "Stress from impact of an elastic sphere on a solid rod", href: `${gh}/Stress-from-Impact-of-an-Elastic-Sphere-against-a-Solid-Rod` },
  { title: "Velocity measurement system (Arduino)", href: `${gh}/Control-code-for-Velocity-Measurement-system` },
  { title: "Precise control of a stepper motor", href: `${gh}/Precise-control-of-stepper-motor` },
  { title: "Mohr's circle for 2D and 3D stress tensors", href: `${gh}/Mohr-s-circle---Graphical-representation-for-2D-and-3D-stress-tensors` },
  { title: "Tensile test: calculations for bars in tension", href: `${gh}/Tensile-test---Calculations-for-bars-in-tension` },
];

export const web = [
  {
    title: "Bharatiya Nagarika",
    when: "Dec 2023 – present",
    text: "Full-stack development and maintenance: HTML, Tailwind CSS, JavaScript and PHP.",
    href: "https://bharatiyanagarika.com/",
  },
  {
    title: "ZHUOJIA 卓嘉 Engineering & Consultants",
    when: "2026",
    text: "Company website in English and Chinese, built with TypeScript and Vite.",
    href: "https://edgar-mendonca.github.io/zhuojia/",
  },
];
