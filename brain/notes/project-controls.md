---
project: package-project-controls
area: project-controls
---
# Project controls for equipment packages

## Weighted progress

Progress for an equipment package is the sum of each item's weight times its progress. Items carry weights by
value and effort (the compressor, dry gas seals and gearbox weigh most; small electrical items least), and each
item moves through phases that carry their own weights: material requisition, request for quotation, technical bid
evaluation, purchase order, design, procurement, manufacturing (the largest share), factory acceptance test,
packing and delivery. A procurement status register lists each tag with its vendor, equipment, weight and the
planned and actual date of every phase, so planned and actual progress can be compared on the same basis.

The formula has to agree with how cells store progress (fractions or 0–100) and cover every phase. Status bands
such as on track, at risk and delayed are a reporting convention, not a substitute for schedule variance analysis.

## Project framework

A management framework for a compressor package covers objectives, applicable standards, scope, organisation and
RACI, reporting lines, planning, work breakdown structure, master schedule, milestones, progress measurement, risk,
reporting and HSE. The organisation typically has a project director and project manager, project control,
project engineering with planning and document control, engineering by discipline (process, mechanical,
electrical, instrumentation, structural and piping), procurement with expediting and logistics, QA/QC with
inspection, welding and testing, manufacturing, and commissioning.

## Reports and dashboards

Weekly and monthly reports; engineering, procurement and manufacturing progress; inspection and test reports;
engineering document S-curves; planned against actual progress and variance; traffic-light status; supplier
scorecards; Kanban views of document status. Templates come with both the underlying registers and the management
summary.

## HSE reporting

A safety pyramid from the most serious incidents down to near misses, unsafe acts and unsafe conditions; lost-time
and total recordable incident rates against targets; week-, month- and project-to-date figures with man-hours.
Note that FAT means factory acceptance test elsewhere in package work, so the two contexts must not be mixed.

## Risk and audit

Risk matrices, categories and heat maps for package components. Internal quality audits covering engineering,
procurement, manufacturing, inspection, testing, sub-vendor management and quality records, kept general rather
than tied to one corrective action.

## Scheduling software references

Detailed references to desktop scheduling tools: task information, fields and formulas, graphical indicators, bar
styles, timescales, page setup, reports, network diagrams, team planner and resource views; and for enterprise
schedulers, activities, layouts, activity codes, schedule options and schedule checks. An open, self-hosted project
control application was also documented, with registers, approvals, baselines, multiple schedules, Gantt
forecasting, document cycles, progress curves and backups, using inclusive calendar days and finish-to-start
critical path, and keeping demonstration data separate from real project records.
