# Hermes Project Guidelines

## Overview
Hermes is an API capable of scrapping webpage using AI techniques.

## Coding Standards
- **Language**: Python 3.12+
- **Linter/Formatter**: Ruff. Ensure code passes `ruff check .`
- **Type Hints**: All functions and methods must have type hints.
- **Docstrings**: All modules, classes, and public functions must have docstrings.
- **Dependency Management**: Poetry.

## Design Principles
- **SOLID**: Adhere to SOLID principles. Classes should have a single responsibility.
- **KISS**: Keep It Simple, Stupid. Avoid over-engineering.
- **TDD**: Test-Driven Development. Write tests before implementation when possible.

## Project Structure
- `src/hermes`: Source code.
- `tests`: Tests.

## Testing
- Use `pytest` for testing.
- Write tests for new features.

## AI Scraper Implementation
- The scraper uses an LLM to parse natural language rules.
- Clean HTML content before sending to LLM to optimize token usage.
- Use `pydantic` for structured output when possible.
