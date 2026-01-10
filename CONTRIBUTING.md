
# Contributing to Bambara Text Normalizer

Welcome to the Bambara Text Normalizer! We're thrilled you're interested in contributing to our mission of advancing NLP tools for Bambara (Bamanankan). Whether you're fixing bugs, adding features, improving linguistic rules, or enhancing documentation, your contributions are valuable. This guide will help you get started. Let's build something awesome together! 🫂

## Table of Contents

1. [Getting Started](#getting-started)
   - [Prerequisites](#prerequisites)
   - [Setting Up the Development Environment](#setting-up-the-development-environment)
2. [How to Contribute](#how-to-contribute)
   - [Reporting Bugs](#reporting-bugs)
   - [Suggesting Features](#suggesting-features)
   - [Submitting Pull Requests](#submitting-pull-requests)
3. [Code Style and Quality](#code-style-and-quality)
4. [Testing](#testing)
5. [Community Guidelines](#community-guidelines)
6. [Versioning and Releases](#versioning-and-releases)


## Getting Started

### Prerequisites

To contribute, you'll need:
- **Python 3.8+**: Ensure you have a compatible Python version installed.
- **Git**: For cloning the repository and managing version control.
- **pip** or **uv**: For installing dependencies.

### Setting Up the Development Environment

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/sudoping01/bambara-text-normalization.git
   cd bambara-text-normalization
   ```

2. **Create a Virtual Environment** (recommended):
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. **Install Dependencies**:
   Install the package in editable mode with development dependencies:
   ```bash
   pip install -e .
   pip install -r dev-requirements.txt
   ```
   Alternatively, use `uv` for faster dependency resolution:
   ```bash
   uv pip install -e .
   uv pip install -r dev-requirements.txt
   ```

4. **Set Up Pre-Commit Hooks** (optional but recommended):
   Install pre-commit to enforce code style:
   ```bash
   pre-commit install
   ```

5. **Verify Your Setup**:
   Run the test suite to ensure everything works:
   ```bash
   pytest tests/ -v
   ```

## How to Contribute

### Reporting Bugs

Found a bug? Help us fix it!
- Check the [issue tracker](https://github.com/sudoping01/bambara-text-normalization/issues) to ensure the bug hasn't been reported.
- Submit a new issue with:
  - A clear description of the bug.
  - Steps to reproduce it.
  - Expected and actual behavior.
  - Input text and output (if applicable).
- Tag `@sudoping01` in your issue for faster review.

### Suggesting Features

Have an idea to improve the normalizer?
- Submit a feature request as an issue.
- Describe:
  - The problem your feature solves.
  - Your proposed solution.
  - Any linguistic justification (for normalization rules).
- Tag `@sudoping01` to ensure visibility.

### Submitting Pull Requests

Ready to contribute code? Here's how:

1. **Fork the Repository**:
   Fork the repo and clone your fork:
   ```bash
   git clone https://github.com/your-username/bambara-text-normalization.git
   ```

2. **Create a Branch**:
   Create a descriptive branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/bug-description
   ```

3. **Make Changes**:
   - Follow the [code style guidelines](#code-style-and-quality).
   - Add or update tests in `tests/` for any new functionality.
   - Update `README.md` if your changes affect usage.

4. **Run Code Style Checks**:
   Ensure your code passes linting:
   ```bash
   ruff check .
   isort . --check-only
   ```
   To auto-fix issues:
   ```bash
   ruff check . --fix
   isort .
   ```

5. **Run Tests**:
   Verify all tests pass:
   ```bash
   pytest tests/ -v
   ```

6. **Commit Your Changes**:
   Use clear, conventional commit messages:
   ```bash
   git commit -m "feat: add ordinal number support"
   git commit -m "fix: correct k' disambiguation for 'ye' postposition"
   git commit -m "docs: update contraction mode examples"
   git commit -m "test: add edge cases for number normalization"
   ```

7. **Push and Create a Pull Request**:
   ```bash
   git push origin feature/your-feature-name
   ```
   - Describe your changes and their purpose.
   - Link to related issues.
   - Tag `@sudoping01` for review.

8. **Address Feedback**:
   Respond to reviewer comments and make necessary updates. GitHub Actions will automatically run linting and tests on your PR.

## Code Style and Quality

We use the following tools to maintain consistency:

| Tool | Purpose | Command |
|------|---------|---------|
| **Ruff** | Linting and formatting | `ruff check .` |
| **isort** | Import sorting | `isort . --check-only` |
| **pytest** | Testing | `pytest tests/ -v` |

Before submitting a pull request:
```bash
# Check for issues
ruff check .
isort . --check-only

# Auto-fix issues
ruff check . --fix
isort .

# Run tests
pytest tests/ -v
```

## Testing

All contributions should include tests:

- Add tests in `tests/test_normalizer.py` for new features or bug fixes.
- Follow existing test patterns (see `TestContractionModes`, `TestNumberNormalization`).
- Ensure all tests pass before submitting:
  ```bash
  pytest tests/ -v --tb=short
  ```

**Test naming convention**:
```python
class TestYourFeature:
    def test_feature_basic_case(self):
        ...
    
    def test_feature_edge_case(self):
        ...
```

**Current test coverage**: 114 tests passing

## Community Guidelines

We value a welcoming and inclusive community. Please:
- Be respectful and constructive in issues, pull requests, and discussions.
- Follow the [Code of Conduct](CODE_OF_CONDUCT.md) if available.
- Reach out to `@sudoping01` for questions or guidance.

## Versioning and Releases

We use [Semantic Versioning](https://semver.org/) (MAJOR.MINOR.PATCH):

| Change Type | Version Bump | Example |
|-------------|--------------|---------|
| Breaking changes | MAJOR | 2.0.0 → 3.0.0 |
| New features | MINOR | 2.0.0 → 2.1.0 |
| Bug fixes | PATCH | 2.0.0 → 2.0.1 |

To create a release:
1. Update version in `src/bambara_normalizer/__init__.py`.
2. Update `CHANGELOG.md` (if available).
3. Tag the release:
   ```bash
   git tag v2.1.0
   git push origin v2.1.0
   ```

---

**Thank you for contributing to Bambara Text Normalizer! Your efforts help advance NLP for Bambara and other African languages. 🇲🇱 ❤️**

<p align="center">
    <a href="https://github.com/MALIBA-AI">MALIBA-AI</a>
</p>
