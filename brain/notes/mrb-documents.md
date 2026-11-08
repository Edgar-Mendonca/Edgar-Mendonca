---
project: mrb-documents
area: documentation
---
# Manufacturing record books and document assembly

## The workflow

A manufacturing record book (MRB) combines certificates, inspection and test records, manuals and supporting
documents for one piece of equipment into one coherent PDF. The steps: combine the source PDFs in the right order,
keep every page readable, give each section a meaningful title, add a visible table of contents, add PDF bookmarks
and clickable links from the contents to each section, keep page numbers and link targets right after inserting
pages, and deliver one downloadable file. Never forget the bookmarks. Where source records are in another language,
the book can be bilingual.

## Typical packages

For the ADNOC Sahil Phase 3 EGC package: EagleBurgmann dry gas seals; the SBW lube oil system; the EagleBurgmann
seal gas console and booster; the Flender gearbox; Kelvion lube oil air coolers; Titania Aero proximity probes;
junction boxes; valves; lifting beams; venturi meters; online cleaning devices; nitrogen-purged enclosures; and
instruments such as Siemens SITRANS P pressure transmitters, temperature transmitters, pressure gauges, resistance and bimetallic
thermometers, and thermowells.

## Large files

Books can run to thousands of pages and hundreds of megabytes with over a hundred bookmarks, so they are built with
scripts rather than by hand: Python with PyMuPDF to merge files, export and import bookmarks as CSV, generate a
contents page and create internal links. Outputs keep the table of contents and linked contents as separate
versions.

## Inspection records

Inspection stamps and signatures (manufacturer QC and third-party inspection bodies such as LRQA and Intertek) can be
extracted and presented from the source records for review. Material certificates follow EN 10204 (3.1 or 3.2). This is
document processing only: an inspection record belongs to the item it was issued for and must never be reused or
implied for anything else.
