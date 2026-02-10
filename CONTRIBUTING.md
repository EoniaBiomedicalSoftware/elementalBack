# Contributing to Elemental Backend

Thank you for your interest in contributing to Elemental Backend! This document provides guidelines and information to help you get started.

## 🎯 Areas We Need Help With

We're actively looking for contributors in these areas:

### High Priority
- **CLI Interface**: Build a custom CLI framework from scratch (currently doesn't exist – great opportunity!)
- **Project Generator (CLI)**: Create a scaffolding tool to bootstrap new projects using Elemental
- **Domain Modules Examples**: Create reference implementations (Users, Posts, Tasks, etc.)
- **Testing**: Improve test coverage, especially integration and E2E tests
- **Documentation**: Expand guides, add tutorials, improve code comments

### Medium Priority
- **DevOps**: Docker setup, CI/CD pipeline configuration
- **Performance**: Optimization, benchmarking, caching strategies
- **Security Audits**: Review authentication, authorization, and data validation

## 🚀 Getting Started

### Prerequisites
- Python 3.13+
- [uv](https://github.com/astral-sh/uv) package manager
- Git

### Setup Development Environment

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/EoniaBiomedicalSoftware/elementalBack
   cd elementalBack
   ```

2. **Install dependencies**
   ```bash
   uv sync --all-groups
   ```

3. **Create your local configuration**
   ```bash
   # Modify
   settings.dev.toml
   ```

4. **Run the application**
   ```bash
   # Web mode
   uv run python main.py web
   uv run python main.py
   
   # CLI mode (when implemented)
   uv run python main.py cli [command]
   ```

5. **Run tests**
   ```bash
   uv run pytest
   ```

---

## 🛠️ CLI Interface Development (Open Contribution!)

### Current State

**The CLI interface doesn't exist yet!** This is a perfect opportunity for contributors to design and implement it from scratch.

### Why We're Not Using Typer

We evaluated Typer but decided against it for these reasons:

- **Limited async support**: Difficult to integrate with our async-first architecture
- **Over-abstraction**: Too much magic for simple command routing
- **Bundle size**: Unnecessary overhead for a framework component

### What We're Looking For

We need a lightweight, async-native CLI interface. Here's what we envision:

**Design Principles:**
- **Minimal dependencies**: Use only stdlib where possible
- **Async-first**: Full support for async command handlers
- **Type-safe**: Leverage Python 3.13+ type hints
- **Modular**: Easy to extend with custom commands
- **Self-documenting**: Auto-generate help from docstrings and type hints

### 🎯 Project Generator CLI (High Priority)

One of the most important features to build is a **project generator** that scaffolds new projects using Elemental Backend as a base.

---

## 📋 Development Guidelines

- **Type hints**: Use them everywhere. We target Python 3.13+ features
  ```python
  # Good
  async def get_user(user_id: int) -> User | None:
      ...
  
  # Avoid
  async def get_user(user_id):
      ...
  ```

- **Docstrings**: Use Google-style docstrings for public APIs
  ```python
  def process_data(data: list[str]) -> dict[str, int]:
      """Process input data and return statistics.
      
      Args:
          data: List of strings to process
          
      Returns:
          Dictionary with processing statistics
          
      Raises:
          ValueError: If data is empty
      """
  ```

### Project Structure Philosophy

Our architecture follows these principles:

1. **`app/elemental/`** - Core framework code (minimal external dependencies)
   - Should be reusable across any project using Elemental
   - No business logic here
   - Pure utilities, security, logging, exceptions

2. **`app/infrastructure/`** - External integrations (secondary adapters)
   - Database, email, file storage, OAuth providers
   - Each integration should be swappable

3. **`app/gateways/`** - Entry points (primary adapters)
   - `web/`: FastAPI routes, middlewares
   - `cli/`: Command-line interface (to be implemented)
   - These consume domain logic, never implement it

4. **`app/src/`** - Business domains
   - Self-contained modules following clean architecture
   - Each module can have its own internal structure

### Testing Strategy

We follow a **testing pyramid**:

```
        /\
       /E2E\      (Fewer, high-value)
      /------\
     /  INT   \   (Moderate amount)
    /----------\
   /    UNIT    \ (Most tests here)
  /--------------\
```

**Unit Tests** (`test/unit/elemental/`)
- Test `app/elemental/` utilities in isolation
- Fast, no I/O, no database
- Mock external dependencies

**Integration Tests** (`test/integration/`)
- Test `app/infrastructure/` and `app/src/` with real database
- Use test database
- Verify repositories, services work correctly

**E2E Tests** (`test/e2e/`)
- Test complete workflows via HTTP API
- Use TestClient from FastAPI
- Simulate real user interactions
## 🔄 Contribution Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/amazing-feature
# or
git checkout -b fix/bug-description
```

Branch naming:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation only
- `refactor/` - Code refactoring
- `test/` - Adding tests

### 2. Make Your Changes

- Write code following our style guidelines
- Add/update tests
- Update documentation if needed
- Keep commits atomic and well-described

**Commit Message Format:**
```
type(scope): short description

Longer description if needed.

Fixes #123
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`

Examples:
```
feat(cli): add project generator command
fix(auth): resolve token expiration bug
docs(readme): update installation instructions
test(users): add integration tests for user service
```

### 3. Run Quality Checks

Before pushing:
```bash
# Format code
uv run ruff format .

# Run linter
uv run ruff check .

# Run tests
uv run pytest

# Type checking (if mypy configured)
uv run mypy app/
```

### 4. Push and Create PR

```bash
git push origin feature/amazing-feature
```

Then open a Pull Request on GitHub with:
- **Clear title** describing the change
- **Description** explaining what and why
- **Link to related issues** (e.g., "Closes #42")
- **Screenshots/examples** if UI/CLI changes

### PR Review Process

1. Automated checks must pass (when CI is set up)
2. At least one maintainer review is required
3. Address review comments
4. Maintainer merges when approved

---

## 🎨 Creating a New Domain Module

Want to add an example domain? Here's the structure we follow:

### Required Structure

The **only mandatory files** for route discovery are:

```
app/src/tasks/
├── gateways/
│   ├── __init__.py              # Required
│   └── api/
│       ├── __init__.py          # Required
│       ├── router.py            # Required - main API router
│       └── v1/
│           ├── __init__.py
│           └── endpoints.py     # Your actual route handlers
```

**Required `router.py` format:**
```python
# app/src/tasks/gateways/api/router.py
from fastapi import APIRouter
from .v1 import router as v1_router

api_router = APIRouter()
api_router.include_router(v1_router)
```

This structure allows automatic route discovery by the framework.

### Recommended Full Structure

While only the gateway structure is required, we recommend organizing your module following clean architecture principles:

```
app/src/tasks/
├── app/                    # Application layer (use cases, services)
│   ├── __init__.py
│   ├── services.py        # Business logic orchestration
│   └── use_cases.py       # Specific application use cases
├── domain/                 # Domain layer (business rules, entities)
│   ├── __init__.py
│   ├── entities.py        # Domain entities (pure business objects)
│   ├── value_objects.py   # Immutable value objects
│   └── events.py          # Domain events
├── infrastructure/         # Infrastructure layer (external concerns)
│   ├── __init__.py
│   ├── models.py          # SQLAlchemy models (database)
│   ├── repository.py      # Data access implementation
│   └── external_api.py    # Third-party API clients
└── gateways/              # Gateways layer (interfaces) - REQUIRED
    ├── __init__.py        # REQUIRED
    └── api/               # API gateway
        ├── __init__.py    # REQUIRED
        ├── router.py      # REQUIRED - main router
        ├── v1/            # API version 1
        │   ├── __init__.py
        │   ├── endpoints.py
        │   └── schemas.py # Pydantic request/response models
        └── dependencies.py
```

### Key Architectural Principles

1. **Dependencies flow inward**: 
   - Gateways → App → Domain
   - Infrastructure is injected where needed
   - Domain has no dependencies on outer layers

2. **Domain is the core**:
   - Business rules live in `domain/`
   - No framework dependencies in domain layer
   - Pure Python business logic

3. **Application orchestrates**:
   - `app/services.py` coordinates domain and infrastructure
   - Implements use cases
   - Transaction management

4. **Gateways are adapters**:
   - Convert external requests to domain operations
   - HTTP → Domain entities
   - Return domain results as HTTP responses

5. **Infrastructure is pluggable**:
   - Database can be swapped
   - External APIs can be mocked
   - No business logic here

---

## 📖 Documentation

### What to Document

- **New features**: Update README.md or create guides in `/docs`
- **API changes**: Update docstrings and OpenAPI descriptions
- **Architecture decisions**: Consider adding ADRs (Architecture Decision Records)
- **CLI commands**: Update this file with new command examples

## ❓ Questions or Issues?

- **Found a bug?** Open an [issue](https://github.com/EoniaBiomedicalSoftware/elementalBack/issues)
- **Have a question?** Start a [discussion](https://github.com/EoniaBiomedicalSoftware/elementalBack/discussions)
- **Want to propose a feature?** Open an issue with `[FEATURE]` in the title

---

## 📜 Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

---

## 🙏 Thank You!

Every contribution, no matter how small, helps make Elemental Backend better. We appreciate your time and effort!

Happy coding! 🚀