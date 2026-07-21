# Contributing

Agent Playbook is maintained as a **personal open-source project** by [zllabs](https://github.com/zllabs).

**External contributions (pull requests) are not accepted at this time.** You are welcome to use, fork, and adapt the project under the [MIT license](LICENSE). Recognition of the original work stays with this repository and its author.

## Using the project

See the [README](README.md) quick start. Run both the API and web app locally:

```bash
cd apps/api && python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

cd apps/web && npm ci && npm run dev
```

Open http://localhost:5173 (API must be running on port 8000).

## Forks and local changes

If you fork or modify a copy for yourself:

- Keep the MIT license and copyright notice.
- Catalog entries must remain metadata-only — see [docs/adding-resources.md](docs/adding-resources.md).
- Run tests before relying on changes:

```bash
python3 -m tests
cd apps/api && .venv/bin/python test_recommend.py
cd apps/web && npm run build
```

## Feedback

Issues may be opened for bugs or ideas, but there is no commitment to respond or implement requests.

## Security

See [SECURITY.md](SECURITY.md).
