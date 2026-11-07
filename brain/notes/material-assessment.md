---
project: material-assessment
area: materials
---
# Material assessment for compressor service

## Two tools, not one

A materials-selection tool ranks candidate materials on property charts (now Datum Atlas). A material-assessment
tool answers a different question: is the material chosen for this stage and component suitable for this gas?
They share a materials database and plotting, but they are separate jobs.

## Assessment inputs

H₂S and CO₂ partial pressures; chloride concentration; pH; oxygen; droplet size; wet or dry service; water dew
point; each stage's temperature and pressure; and the material of each component (casing, impellers, shaft, dry gas
seal parts, console).

## Outputs

An adjustable saturation and dew-point curve; a wet and dry phase map; sulfide stress cracking (SSC) domain overlays
with the stage conditions plotted on them; and risk bars per component.

## The database

Carbon steel for low-temperature service (standard and sour-service variants), quenched and tempered alloy steel,
316/316L stainless, precipitation-hardened 17-4PH, duplex and super duplex stainless, nickel alloys 625 and 718, and
C-276. Each record holds corrosion limits (H₂S and CO₂ partial pressure, chlorides, pH, SSC domain, sour-service
compliance, pitting resistance equivalent number), mechanical and physical properties, fabrication notes and a cost
factor. A sour-service flag in a database is never a qualification by itself: it depends on product form, heat
treatment, hardness and the actual service conditions.

## Interfaces tried

A desktop Tkinter version, then a browser version with inputs, graphs, a materials database and an about tab, with
tooltips, PNG and SVG export, example cases, a materials editor, local saving and mobile support. The direction
after that was a stronger Python version with NumPy, SciPy and Matplotlib, still reachable in a browser.

## Selection charts

Selection indices such as E/ρ, σ/ρ, stiffness-limited design and PREN, with clear controls to choose them, consistent
colours, families of materials and export. These requirements carried into Datum Atlas.
