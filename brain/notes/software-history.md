---
project: datum
area: software-platform
---
# How the software family came about

## The ambition

One family of open-source tools for engineers, scientists, researchers and analysts, with one brand, one way of
working, a separate repository per app under the MIT licence, and a launcher that installs and updates each app.
Most of the apps grew out of real work: scheduling and procurement tracking, material assessment, experimental
signal processing, record-book assembly, plotting and engineering calculation.

## Names along the way

The core set settled on Plan, Atlas, Plot and Calc, then grew with Sim, Mesh, Pipe, Schema and Layout. Earlier
directions included separate apps for thermowell wake frequency and for SHPB pulse analysis, which were later
left out of the core set.

## Launcher and distribution

A desktop launcher showing every app with Install and Update buttons depending on whether it is installed and
whether a newer release exists. Technologies weighed along the way: Rust, Python with JavaScript, Electron, Tauri,
static web hosting and Next.js; the family settled on Rust with Tauri 2 and SolidJS, with Python bundled where an
app needs science libraries.

## Look

Swiss/International Typographic Style, technical-editorial and scientific minimalism: vector logos, one family mark,
consistent colours, mobile support for anything in a browser, and a useful home page before the working screens.

## Plot, Plan, Calc and Sim ambitions

Plot: multi-axis graphs, linear to logistic and nonlinear fits, ANOVA and t-tests, bar, box, violin, scatter and line
plots, multiple sheets, CSV and Excel import, transforms, error bars, smoothing, themes, LaTeX labels and
publication exports. Plan: tasks, dependencies, Gantt, WBS, baselines, calendars and resources, dashboards, issues,
cost, progress and reports, exchanging files with common schedulers, without forcing every project into one
industry's structure. Calc: a library of engineering formula cards. Sim: block diagrams with later physical
components, parameter sweeps, sensitivity, linearisation, frequency-response plots, PID tuning and model fitting,
with examples such as compressor anti-surge, pump–pipe–tank, DC motor PID, heat exchanger, mass–spring–damper and
cruise control.
