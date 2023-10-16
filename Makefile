commit:
	black .
	ruff . --fix
	black .
	ruff . --fix

help:
	@echo "Available targets:"
	@echo "\033[33mcommit\033[0m      : Run all tests, linting, and formatting tools, incl. pre-commit hooks"
	@echo "\033[34mhelp\033[0m        : Show this helper message"

.PHONY: commit help
