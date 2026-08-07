# Contributing Guide

This document explains how to contribute to MediGuard, set up local development, and run tests.

## Getting Started

1. Fork the repository.
2. Clone your fork locally.
3. Install backend and frontend dependencies.
4. Create environment files and start the app.

## Development Workflow

### Backend

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install
```

### Start services

```bash
cd backend
python main.py
```

```bash
cd frontend
npm run dev
```

## Branching and Pull Requests

- Create a descriptive branch name: `feature/medication-api`, `fix/auth-token`, `docs/setup`.
- Make focused commits with clear messages.
- Rebase or merge the latest `main` before opening a PR.
- Include testing details and screenshots if applicable.

## Testing

### Backend tests

```bash
cd backend
pytest
```

### End-to-end tests

```bash
cd backend
python e2e_test.py
```

### Frontend checks

```bash
cd frontend
npm run lint
npm run build
```

## Code Style

- Python: follow PEP 8 and idiomatic Python practices.
- TypeScript: use strict typing where appropriate.
- Use descriptive variable and function names.
- Keep UI components reusable and accessible.

## Documentation

- Keep docs up to date with architecture or API changes.
- Add or update docs in the `docs/` folder when new features are introduced.
- Use the existing `README.md` for high-level product information.

## Reporting Issues

- Open issues for bugs, feature requests, or documentation gaps.
- Provide reproduction steps and expected vs actual behavior.

## Notes

- Do not commit secrets, API keys, or `.env` files.
- Use `backend/.env` and `frontend/.env.local` locally only.
- Add any new required environment variables to `.env.example`.
