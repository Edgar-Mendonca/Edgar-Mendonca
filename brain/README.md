# The brain

A neural network trained on everything Edgar has built, written and decided: every README, memory file,
changelog, plan and design guide of the Datum apps and CentriForge, the research write-ups, and the notes in
[`notes/`](notes). It is the starting point for an AI agent that knows Edgar's work: given a task in plain words,
it says which project and area of work it belongs to, what sort of knowledge it needs, and which past decisions,
releases and write-ups are related.

Written from scratch in Python with NumPy only: forward pass, backpropagation and the Adam optimiser are in
[`nn.py`](nn.py), checked against finite differences in [`tests/test_nn.py`](tests/test_nn.py).

## The network

```
text ─► words and word pairs, hashed into 8192 TF-IDF features
     ─► dense 128, ReLU, dropout 0.3
     ─► dense 64, tanh  ──────────────►  the embedding: one point in Edgar's work-space
     ─► three softmax heads, trained together
          project  datum-pipe, centriforge, shpb, compressor-package, …   (16)
          area     piping, rotating-equipment, impact-mechanics, …         (12)
          kind     decision, release, plan, session, research, note, …     (9)
```

About 1.06 million parameters, trained in about 15 seconds on a laptop CPU. Training the three heads together
makes the shared 64-number embedding sort text by subject, project and kind at once; related work is found by
closeness in that embedding, steadied by plain word overlap.

**Current model** ([`model/report.json`](model/report.json)): 2,010 chunks (309k words) from 14 sources.
On 301 held-out chunks it names the right project 93% of the time and the right area 93% (always guessing the
largest class: 16%), and the kind of knowledge 87% (24%). On 15 plain-language routing tasks
([`tests/probes.json`](tests/probes.json)) it routes 13 correctly; the misses are a curve-fitting task sent to the
tube study instead of Datum Plot, and a pipe-routing task sent to Datum Pipe instead of Datum Layout.

## Use it

```bash
pip install numpy
python brain/brain.py ask "vendor sent a dry gas seal datasheet, review it against API 617"
python brain/brain.py ask --json "…"     # for an agent: probabilities and related chunks as JSON
python brain/brain.py profile            # the evidence of work, area by area (model/PROFILE.md)
```

```
project  compressor-package 51%   centriforge 31%   stress-waves 5%
area     rotating-equipment 93%   impact-mechanics 2%   process-design 2%
kind     note 51%   feature 30%   plan 13%

related work:
  [0.60] compressor-package · note  —  local/brain/notes/compressor-package.md
         Export Gas Compressor Package (API 617) › Sub-vendor interfaces. - ABB: main motor, …
```

## See it

```bash
python brain/viewer.py     # writes model/viewer.html: the map of every note and the network, running in the page
```

The page is not committed (it is in `.gitignore`); it is published as a private page only Edgar can open. The map
places every note by the network's 64-number embedding, laid out in 2D with t-SNE; the Ask box runs the same network
in the browser (8-bit first layer, same answers as `brain.py ask` on all routing probes).

## Teach it

1. Add what you do to [`notes/`](notes): one Markdown file per project, meeting or week, with `project:` and
   `area:` at the top (see [`notes/README.md`](notes/README.md)). New projects become new classes.
2. Add new repositories to [`sources.json`](sources.json).
3. Rebuild and retrain, then commit `data/` and `model/`:

```bash
python brain/brain.py collect      # clones or refreshes the repositories into ~/.cache/edgar-brain
python brain/brain.py train
python brain/tests/probe.py        # routing check
python brain/tests/test_nn.py      # gradient check
```

## What it knows, and what it does not yet

[`model/PROFILE.md`](model/PROFILE.md) counts the evidence by area. Today the Datum apps dominate, because their
memory files and changelogs record every decision and release. The compressor-package work and the research are
about 3% of the corpus between them: the brain will route those tasks correctly, but it has little of that work to
recall. Notes about the day job (vendor reviews, deviations, technical queries, lessons learned) are what will
make it useful for day-to-day work.

The profile measures how much is written down, not skill. The network classifies and retrieves; it does not
generate text. For the agent, it is the memory and the router: an LLM reads the related chunks it returns and does
the writing.
