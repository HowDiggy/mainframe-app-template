# Mainframe Golden Application Template

The standard foundation for building and deploying autonomous agent microservices, business ideas, and tools on `mainframe` (`192.168.13.100`).

---

## Key Architectural Features

- **Modern Python Foundation:** Python 3.13 / 3.15 + Poetry + Ruff + strict `src/` layout.
- **Design by Contract (DbC):** Rigorous type annotations and explicit pre/post-condition docstrings.
- **Automated Ephemeral PR Previews:** Opening a PR automatically triggers an ArgoCD `ApplicationSet` to deploy an isolated environment at `https://<app>-pr-<num>.paulojauregui.com` with Let's Encrypt TLS.
- **Secure Runtime:** Multi-stage non-root container execution (`UID 10001`), Kubernetes Gateway API HTTP routing via Cilium eBPF, and zero-dependency unit tests.

---

## Quickstart

### 1. Run Tests Locally
```bash
PYTHONPATH=src python3 -m unittest discover tests -p "*unittest.py"
```

### 2. Run the Service Locally
```bash
poetry install
poetry run python -m mainframe_template.main
```
The API serves at: `http://localhost:8000/`

---

## For AI Coding Agents
See [AGENTS.md](AGENTS.md) for architectural invariants, testing recipes, and GitOps standards.
