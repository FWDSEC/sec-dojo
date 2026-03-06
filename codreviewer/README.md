### Code Review Challenges (Flask)

A tiny Flask app that lets you browse code review challenges with the same scenario shown in multiple languages (C++, Python, Java, TypeScript) with syntax highlighting.

### Run it locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open `http://127.0.0.1:8000`.

### Add more challenges

Edit `challenges.py` and add a new entry to `_CHALLENGES`:

- `id`: integer challenge number
- `title`: short title
- `description`: short prompt text
- `snippets`: code strings keyed by `cpp`, `python`, `java`, `typescript`

### Syntax highlighting

Syntax highlighting is provided by `highlight.js` loaded from a CDN in `templates/index.html`.

