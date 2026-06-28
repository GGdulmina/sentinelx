# Contributing to SentinelX

We welcome contributions to SentinelX! Please follow these guidelines to ensure a smooth contribution process.

## How to Contribute

1. **Fork the Repository**: Create a personal copy of the repository.
2. **Create a Feature Branch**: Work on your changes in a descriptive branch.
   ```bash
   git checkout -b feature/my-new-feature
   ```
3. **Write Code & Verify Syntax**: Ensure your changes adhere to standard coding practices.
   ```bash
   ./manage.sh lint
   ```
4. **Write Tests**: Add unit or integration tests in the `tests/` directory for any new logic or bug fixes.
5. **Run the Test Suite**: Verify that all tests pass.
   ```bash
   ./manage.sh test
   ```
6. **Submit a Pull Request**: Submit your pull request with a clear description of the problem and your solution.

## Coding Standards

- Follow PEP 8 style guidelines.
- Use explicit type hints in function signatures.
- Avoid using greedy `.*` patterns in regular expressions to prevent ReDoS.
- All extracted string fields from logs must be validated and sanitized using `core.parser.sanitize_input`.
- Use the standard `logging` library instead of `print` statements in core modules.

## Testing Guidelines

- All tests must pass before submitting a pull request.
- Test coverage should be maintained or increased.
- Use `pytest` for all test cases.
- Use parameterized tests where appropriate (e.g., testing multiple parser patterns).
