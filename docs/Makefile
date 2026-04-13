# Makefile for wsqlite documentation

PROJECT = wsqlite

.PHONY: html clean serve view livehtml doctest linkcheck

# Build HTML documentation
html:
	sphinx-build -b html . _build/html
	@echo "Documentation built in _build/html"

# Build HTML with warnings
html-dev:
	sphinx-build -b html . _build/html

# Clean build artifacts
clean:
	rm -rf _build
	rm -rf .doctrees
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "Build artifacts cleaned"

# Build and serve documentation
serve: html
	@echo "Starting web server at http://localhost:8000"
	@echo "Press Ctrl+C to stop"
	cd _build/html && python -m http.server 8000

# Build and open in browser
view: html
	@if command -v xdg-open > /dev/null; then \
		xdg-open _build/html/index.html; \
	elif command -v open > /dev/null; then \
		open _build/html/index.html; \
	else \
		echo "Open _build/html/index.html in your browser"; \
	fi

# Auto-build with live reload
livehtml:
	sphinx-autobuild . _build/html --port 8000

# Run doctests
doctest:
	sphinx-build -b doctest . _build/doctest

# Check links
linkcheck:
	sphinx-build -b linkcheck . _build/linkcheck

# Help
help:
	@echo "Available targets:"
	@echo "  html       - Build HTML documentation"
	@echo "  html-dev   - Build HTML (show warnings)"
	@echo "  clean      - Clean build artifacts"
	@echo "  serve      - Build and serve locally"
	@echo "  view       - Build and open in browser"
	@echo "  livehtml   - Auto-build with live reload"
	@echo "  doctest   - Run doctests"
	@echo "  linkcheck - Check external links"