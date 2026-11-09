# Generative AI for Software Development - course tasks

My repository for the EPAM course "Generative AI for Software Development". I will add every practical task here in its own folder.

## Task 1 - Intro

Folder: [task-01-intro](task-01-intro)

- [research.md](task-01-intro/research.md) - research report on generative AI applications (8 use cases)
- [glossary.md](task-01-intro/glossary.md) - GenAI terms explained in my own words
- [graph/](task-01-intro/graph) - optional subtask, relationship graph between glossary terms and the report
  - `terms_graph.png` - static picture
  - `terms_graph.html` - interactive version (open in browser, hover a term)
  - `term_stats.json` - counts of explicit and implicit mentions per term and per section
  - `terms.json` - patterns used for counting (explicit = the term itself, implicit = same idea in other words)
  - `build_graph.py` - script that generates all of the above

To regenerate the graph after editing the report:

```
cd task-01-intro/graph
pip install matplotlib
python build_graph.py
```
