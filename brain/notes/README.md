# Notes

Your own notes for the brain: one Markdown file per topic, project or week of work. Start each file with
front matter so the brain knows where it belongs:

```markdown
---
project: compressor-package
area: rotating-equipment
---
# What happened / what I decided / what I learned
...
```

`area` must be one of the areas in `../sources.json`. `project` can be new; the network learns it on the next
`python brain/brain.py train`. This file itself is not read.
