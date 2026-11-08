# The brain

A neural network trained on everything Edgar has built, written and decided: every README, memory file,
changelog, plan and design guide of the Datum apps and CentriForge, the documentation written inside their code,
the research write-ups, the work notes in
[`notes/`](notes), and the engineering standards that work relies on ([`standards.json`](standards.json)). It is
the starting point for an AI agent that knows Edgar's work: given a task in plain words, it says which project and
area of work it belongs to, what sort of knowledge it needs, and which past notes, decisions and standards are
related.

Written from scratch in Python with NumPy only: forward pass, backpropagation and the Adam optimiser are in
[`nn.py`](nn.py), checked against finite differences in [`tests/test_nn.py`](tests/test_nn.py).
[`torch_brain.py`](torch_brain.py) loads the same weights into PyTorch for further training on a GPU.

## The network

```
text ─► words and word pairs, hashed into 8,192 TF-IDF features
     ─► dense 768, ReLU, dropout 0.3
     ─► dense 384, ReLU, dropout 0.3
     ─► dense 192, ReLU, dropout 0.3
     ─► dense 128, tanh  ─────────────►  the embedding: one point in Edgar's work-space
     ─► three softmax heads, trained together
          project  datum-pipe, centriforge, shpb, standards, compressor-package, …   (27)
          area     piping, rotating-equipment, project-controls, materials, …        (17)
          kind     decision, release, plan, code, standard, note, research, …      (11)
```

About 6.7 million parameters (`--hidden` and `--emb` change the sizes), trained for 15 epochs in about seven
minutes on a laptop CPU. Questions are short, so the network also trains on short passages of every note. The
answer to a question weighs the network's project probabilities equally with a vote of the five closest notes.

**Current model** ([`model/report.json`](model/report.json)): 2,996 notes (457k words), including 840 notes of
code documentation (Python docstrings and Rust doc comments, at most 300 per repository). On 449 held-out notes it
names the right project 90% of the time and the right area 90% (always guessing the largest class: 20%), and the
kind of knowledge 80% (33%). On 35 plain-language tasks ([`tests/probes.json`](tests/probes.json)) it routes 19
to the expected project: questions that name equipment, sub-vendors or standards route well (for example the KOSO
anti-surge valve and CCC controller to the compressor package, API 613 and API 670 to standards); short, general
questions are often sent to the Datum app that implements the topic. More notes from day-to-day work will help
more than more parameters: a bigger network (50 epochs) scored the same.

## Standards

[`standards.json`](standards.json) lists 70 standards: those cited in the work (API 617, 614, 692, 671, 618, 619,
520, 526; ISA-5.1; ISO 10628-2, 5167, 15156; IEC 60534-2-1; ASME PTC 10, PTC 19.3 TW, Section VIII, B31.3, B31.1,
B16.5, B36.10M; EN 13480-3, 13445, 10365, 1993-1-8; AISC 360 and more) and those around a compressor package: gears
and machinery protection (API 613, 670, 684, 686), pumps and seals (API 610, 682), vibration and balance (ISO
20816, 21940), valve testing and fugitive emissions (ISO 15848-1, MESC SPE 77/312, API 641, 598, 6D, ISO 5208),
certificates and welding (EN 10204, ASME IX, ISO 15614-1, ISO 3834, ISO 9001), painting (ISO 12944, 8501-1, NORSOK
M-501), materials (ASTM A350, A105, A182, A351, A216, A370, B637), hazardous areas and safety (IEC 60079, 60529,
61511), reliability (ISO 14224), the Pressure Equipment Directive and ADNOC AGES. Each becomes a training note with
its title, scope and related standards, and with where it is cited (which projects, how often, in which sections),
worked out from the corpus at every build. Add a standard there and it is learnt on the next build.

## Use it

```bash
pip install numpy
python brain/brain.py ask "what does API 614 cover"
python brain/brain.py ask --json "…"     # for an agent: probabilities and related notes as JSON
python brain/brain.py profile            # the evidence of work, area by area (model/PROFILE.md)
```

## See it

```bash
python brain/viewer.py     # writes model/viewer.html: the whole network, running in the page
```

The page is not committed (it is in `.gitignore`); it is published as a private page. Ask a question and it draws
the whole network for it: every unit of every layer (768, 384 and 192 hidden units, 128 embedding values, 27
projects), lit by its real activation, with the strongest connections between layers and signals pulsing along
them. Under it, the answer and the related notes, and a heat map of every weight matrix (all 6.7 million
parameters, each cell the average of a block). The large matrices travel as 8-bit integers; the page gives the same
answer as `brain.py ask` on every probe.

## What is never learnt

Client, project and supplier names are kept: they are public and they show who the work was done with. Personal
details are not: no e-mail addresses, people's names, document numbers, prices or personal matters. Collection
removes every e-mail address and every word whose fingerprint is in [`redact.json`](redact.json) (SHA-256
fingerprints, so the list names nothing). `--private` still reads Markdown from a git-ignored `brain/private/`
folder for anything that must never be committed, and writes everything trained on it there too.

## Teach it

1. Add what you do to [`notes/`](notes): one Markdown file per project or topic, with `project:` and `area:` at the
   top (see [`notes/README.md`](notes/README.md)). Names of clients and suppliers are fine; keep personal details
   out. New projects become new classes.
2. Add new repositories to [`sources.json`](sources.json) and new standards to [`standards.json`](standards.json).
3. Rebuild and retrain, then commit `data/` and `model/`:

```bash
python brain/brain.py collect      # clones or refreshes the repositories into ~/.cache/edgar-brain
python brain/brain.py train
python brain/tests/probe.py        # routing check
python brain/tests/test_nn.py      # gradient check
```

## Moving to PyTorch

```python
import torch_brain
net, labels = torch_brain.load("brain/model/brain.npz")
```

`torch_brain.BrainNet` has the same layers as `nn.py`; train it further with any PyTorch optimiser and write it
back with `torch_brain.save()`, which keeps the `.npz` layout the other tools read. It was written alongside the
NumPy model but not run here (the session could not install PyTorch), so check it against `brain.py ask` on first
use.

## What it knows, and what it does not yet

[`model/PROFILE.md`](model/PROFILE.md) counts the evidence by area. The Datum apps dominate, because their memory
files and changelogs record every decision and release; day-job work and research are a small share. The profile
measures how much is written down, not skill. The network classifies and retrieves; it does not generate text. For
an agent, it is the memory and the router: a language model reads the related notes it returns and does the
writing.
