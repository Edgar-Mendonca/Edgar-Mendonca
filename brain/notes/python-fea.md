---
project: python-fea
area: structural-fea
---
# Finite-element analysis in Python

## What was tried

A Python finite-element workflow: import a STEP geometry, mesh it with Gmsh, and solve a Poisson problem with an
open-source solver (SfePy, then FEniCS and FEniCSx), with meshio for mesh conversion and PyVista and VTK for
results.

## What went wrong

Example scripts written for older solver versions failed on API changes (missing integrals and problem-definition
functions), editors flagged imports, an optional accelerator library raised warnings, and loading a Gmsh mesh
failed with an index error in the element arrays. The move to FEniCSx went through a Conda environment with an MPI
build and PyVista.

## What helps

A reproducible installation path for Windows, one small example that runs end to end, and explicit handling of
geometry, mesh, boundary markers, solver and visualisation. Check the installed library's version before copying
any example. The same ideas later shaped Datum Mesh, which proves its own answers against benchmarks.
