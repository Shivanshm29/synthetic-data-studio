# Contributing to Synthetic Data Studio

Thank you for your interest in contributing to **Synthetic Data Studio**! We welcome bug reports, feature requests, documentation improvements, and code contributions.

---

## 📋 Code of Conduct

All contributors are expected to uphold our [Code of Conduct](CODE_OF_CONDUCT.md) to ensure an open, welcoming, and harassment-free community.

---

## 🛠 Development Workflow

### 1. Fork & Clone

```bash
git clone https://github.com/<your-username>/synthetic-data-studio.git
cd synthetic-data-studio
```

### 2. Create a Feature Branch

Use descriptive branch names with a prefix:
- `feat/add-new-export-format`
- `fix/datascout-parsing-error`
- `docs/update-api-reference`

```bash
git checkout -b feat/your-feature-name
```

### 3. Setup Local Environment

Follow the [Quickstart Guide](README.md#quickstart) to configure both the FastAPI backend and Next.js frontend environments.

### 4. Running Verification Checks

Before submitting your PR, ensure all tests and type checks pass:

#### Backend:
```bash
cd backend
python -m unittest discover -s tests -p "test_*.py"
```

#### Frontend:
```bash
cd frontend
npx tsc --noEmit
npm run build
```

---

## 📝 Commit Guidelines

We adhere to the [Conventional Commits](https://www.conventionalcommits.org/) standard:

- `feat:` A new feature for the user
- `fix:` A bug fix
- `docs:` Documentation only changes
- `style:` Formatting, missing semi-colons, etc.
- `refactor:` A code change that neither fixes a bug nor adds a feature
- `perf:` A code change that improves performance
- `test:` Adding missing tests or correcting existing tests
- `chore:` Maintenance tasks, dependency updates, tooling

**Example**:
```bash
git commit -m "feat(datascout): add caching layer for Kaggle dataset metadata"
```

---

## 📬 Submitting a Pull Request

1. Push your branch to GitHub:
   ```bash
   git push origin feat/your-feature-name
   ```
2. Open a Pull Request against the `main` branch.
3. Fill out the [Pull Request Template](.github/pull_request_template.md).
4. Address any feedback during code review.
5. Once approved and CI passes, your contribution will be merged!
