# 🤖 AGENTS.md — AI & Agent Onboarding Guide

> **For Coding Agents and Engineers:** Read this document first before proposing or implementing changes. It defines the architectural invariants, engineering standards, testing protocols, and PR preview delivery pipeline for services running on `mainframe`.

---

## 1. Project Mission & Mental Model

This repository is the **Golden Application Template** for new software and business ideas built autonomously by agents. It defines the contract between an autonomous agent's code and `mainframe`'s production Kubernetes environment (`192.168.13.100`):

1. **Inner Loop (In-Sandbox):** Agents implement features, add tests, and verify linting with zero external dependencies.
2. **Review Loop (PR Previews):** Opening a Pull Request automatically triggers GitHub Actions to build `linux/amd64` images, while ArgoCD's `ApplicationSet` provisions an isolated preview namespace (`preview-<app>-pr-<number>`) and Gateway API `HTTPRoute` at `https://<app>-pr-<number>.paulojauregui.com`.
3. **Outer Loop (GitOps Promotion):** Human approval and merge to `main` promotes the service to persistent production and prunes the preview environment.

---

## 2. Architectural Invariants (Non-Negotiable Rules)

When adding or modifying code, preserve these core invariants:

### Rule 1: Strict Modularity & `src/` Layout
* All application source code must live under `src/mainframe_template/` (or your application package name).
* Use **absolute imports exclusively** (e.g., `from mainframe_template.config import get_settings`). Relative imports (`from ..config`) are prohibited.

### Rule 2: Design by Contract (DbC)
* Every public function, class, and method must include a structured Docstring that explicitly defines `Pre-conditions` and `Post-conditions`.
* Full type annotations are mandatory on all parameters and return types.

### Rule 3: Zero-Dependency Fallback Pattern for Fast Unit Tests
* Tests must run deterministically in sub-second time without requiring network connections, external Docker daemons, or heavy binary C-extensions.
* Use Python's standard library `unittest` framework for core business logic validation.

### Rule 4: Clean Container Hygiene
* Containers must execute as a non-privileged user (`USER 10001:10001`). Never run as root.
* All HTTP services must expose `/healthz` (liveness) and `/ready` (readiness) probe endpoints.

---

## 3. Directory Map

```text
mainframe-app-template/
├── AGENTS.md                    ← Invariants & agent instructions (You are here)
├── README.md                    ← High-level service overview
├── pyproject.toml               ← Poetry dependencies & Ruff lint rules
├── Dockerfile                   ← Multi-stage non-root container build (linux/amd64)
├── .github/workflows/
│   └── ci.yml                   ← Lint, test, GHCR build, and Trivy scan pipeline
├── src/
│   └── mainframe_template/
│       ├── __init__.py
│       ├── config.py            ← Typed Settings with environment overrides
│       └── main.py              ← FastAPI / ASGI app with health probes & status API
├── tests/
│   └── test_api_unittest.py     ← Zero-dependency standard library unit tests
└── deploy/
    └── base/
        ├── 01-deployment.yaml   ← Kubernetes Deployment (non-root, port 8000)
        ├── 02-service.yaml      ← ClusterIP Service (port 80 -> 8000)
        ├── 03-httproute.yaml    ← Gateway API HTTPRoute (homelab-gateway)
        └── kustomization.yaml   ← Base Kustomization overlay
```

---

## 4. Local Verification & Testing Recipe

Run the zero-dependency test suite:
```bash
PYTHONPATH=src python3 -m unittest discover tests -p "*unittest.py"
```

Run linting:
```bash
poetry run ruff check .
```

Verify Kustomize manifests:
```bash
kubectl kustomize deploy/base
```

---

## 5. PR Preview & Deployment Protocol

1. Push your feature branch to GitHub (`git push origin feat/your-feature`).
2. Open a Pull Request targeting `main`.
3. GitHub Actions builds the image and pushes `ghcr.io/howdiggy/mainframe-app-template:sha-<short>`.
4. ArgoCD discovers the PR and deploys your environment to `https://mainframe-app-template-pr-<number>.paulojauregui.com`.
5. Human reviews the live preview, verifies changes, and merges into `main`.
