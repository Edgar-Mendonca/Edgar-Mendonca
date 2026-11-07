---
project: shpb
area: impact-mechanics
---
# SHPB data processing: lessons from building the tools

## Raw data

The recorded file had a time column and two gauge channels, incident and transmitted. There was no separate
reflected channel: the incident gauge records both the incident and the reflected pulse, so the reflected window
has to be selected from the incident channel. The processed output has time, incident, reflected and transmitted
columns. Selecting a reflected window from the incident channel is not the same as inventing a reflected signal.

## The workflow

Load the voltage–time data; show the raw incident and transmitted channels; select the incident and reflected
windows from the incident channel and the transmitted window from the transmitted channel; crop and review each
selection; reverse a pulse's polarity where needed; keep the selection and reversal controls in one figure; save
the processed data; smooth with a Savitzky–Golay filter; and compute stress–strain and true stress–strain.

## Errors met along the way

Unsupported widget arguments in Matplotlib selectors; callback signatures that did not match; positional indexing
on sliced pandas Series; a missing reflected column; undefined plot handles; and duplicate selector callbacks
overwriting each other.

## Later ideas

A browser version with input, cropping, results and formula tabs, an example case, mobile support and clear theory,
with Python doing the calculation for accuracy.

## Ball-on-bar reference values

A MATLAB tool for ball-on-bar impact used steel defaults: ball and bar radius 0.02 m, density 8000 kg/m³, Young's
modulus 200 GPa, Poisson's ratio 0.3, a 145 µs window and a 1 m/s impact velocity. These are tool defaults, not
experimental constants.
