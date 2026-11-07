# The brain

A neural network trained on everything Edgar has built, written and decided: every README, memory file,
changelog, plan and design guide of the Datum apps and CentriForge, the research write-ups, the work notes in
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
     ─► dense 512, ReLU, dropout 0.3
     ─► dense 256, ReLU, dropout 0.3
     ─► dense 128, tanh  ─────────────►  the embedding: one point in Edgar's work-space
     ─► three softmax heads, trained together
          project  datum-pipe, centriforge, shpb, standards, mrb-documents, …   (27)
          area     piping, rotating-equipment, project-controls, materials, …      (17)
          kind     decision, release, plan, standard, note, research, …           (10)
```

About 4.4 million parameters (`--hidden` and `--emb` change the sizes), trained in about five minutes on a laptop
CPU. Questions are short, so the network also trains on short passages of every note. The answer to a question
weighs the network's project probabilities equally with a vote of the five closest notes.

**Current model** ([`model/report.json`](model/report.json)): 2,120 notes (318k words). On 316 held-out notes it
names the right project 92% of the time and the right area 93% (always guessing the largest class: 16%), and the
kind of knowledge 77% (29%). On 30 plain-language tasks ([`tests/probes.json`](tests/probes.json)) it routes 21 to
the expected project. Several misses are defensible (a dry-gas-seal review against API 617 goes to the API 617
standard; relief-valve orifice letters go to Datum Schema, which implements API 526).

## Standards

[`standards.json`](standards.json) lists every standard cited in the work: API 617, 614, 692, 671, 618, 619, 616,
611, 612, 661, 520 and 526; ISA-5.1; ISO 10628-2, 5167, 898-1 and 4217; IEC 60534-2-1 and 60034-1; ASME PTC 10, PTC
19.3 TW, Section VIII, Section V, B31.3, B31.1, B16.5 and B36.10M; EN 13480-3, 13445, 10365 and 1993-1-8; NACE
MR0175 / ISO 15156; ASTM B637 and D341; and AISC 360. Each becomes a training note with its title, scope and related
standards, and with where it is cited (which projects, how often, in which sections), worked out from the corpus at
every build. Add a standard there and it is learnt on the next build.

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
the network for that question as nodes and connections: the question's words, the most active units of each hidden
layer, the strongest embedding values and the likeliest projects, every line a real weight × activation, animated
layer by layer. Under it: the answer and the related notes. The two large weight matrices travel as 8-bit integers;
the page gives the same network output as `brain.py ask` on every probe.

## What is never learnt

Notes are written generically: no client, project, supplier or person names, document numbers, e-mail addresses,
places, prices or values from project work. As a safety net, collection removes every e-mail address and every word
whose fingerprint is in [`redact.json`](redact.json) (SHA-256 fingerprints, so the list names nothing).
`--private` still reads Markdown from a git-ignored `brain/private/` folder for anything that must never be
committed, and writes everything trained on it there too.

## Teach it

1. Add what you do to [`notes/`](notes): one Markdown file per project or topic, with `project:` and `area:` at the
   top (see [`notes/README.md`](notes/README.md)). Keep it generic. New projects become new classes.
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
