"""
Sphinx Configuration for wsqlite

Professional documentation configuration with furo theme,
advanced autodoc features, and responsive design.
"""

import os
import sys

# Project metadata
project = "wsqlite"
copyright = "2024, William Steve Rodriguez Villamizar"
author = "William Steve Rodriguez Villamizar"
author_link = "https://es.linkedin.com/in/wisrovi-rodriguez"

version = "1.0.0"
release = "1.0.0"

# Extension configuration
extensions = [
    # Markdown support
    "myst_parser",
    # Documentation generation
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    # UI enhancements
    "sphinx_copybutton",
    "sphinx_sitemap",
    "sphinx.ext.mathjax",
    "sphinx.ext.graphviz",
    # Additional features
    "sphinx.ext.extlinks",
    "sphinx.ext.ifconfig",
]

# Autodoc configuration
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "show-inheritance": True,
    "inherited-members": False,
    "exclude-members": "__weakref__, __dict__, __module__",
}

autodoc_type_aliases = {
    "any": "Any",
    "List": "list",
    "Dict": "dict",
    "Optional": "Optional",
    "Callable": "Callable",
}

# Napoleon extension for Google/NumPy docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_use_returns = True

# Template configuration
templates_path = ["_templates"]
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "**.ipynb",
    "**.mypy_cache",
    "**.pytest_cache",
]

# HTML output configuration
html_theme = "furo"
html_static_path = ["_static"]

html_title = "wsqlite Documentation"
html_short_title = "wsqlite"

# Furo theme options
html_theme_options = {
    "sidebar_hide_name": False,
    "navigation_with_keys": True,
    "top_of_page_button": "edit",
    "pygment_light_style": "monokai",
    "pygment_dark_style": "monokai",
    # Sidebar configuration
    "left_sidebar_end": ["page-toc", "local-toc"],
    "left_secondary_level_indent": 4,
    # Footer configuration
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://github.com/wisrovi/wsqlite",
            "icon": "fab fa-github-square",
        },
        {
            "name": "PyPI",
            "url": "https://pypi.org/project/wsqlite/",
            "icon": "fab fa-python",
        },
        {
            "name": "Author LinkedIn",
            "url": "https://es.linkedin.com/in/wisrovi-rodriguez",
            "icon": "fab fa-linkedin",
        },
    ],
    # Theme colors (customizable)
    "theme_ansi_light": "#4f4f4f",
    "theme_ansi_dark": "#d0d0d0",
}

# HTML context for custom templates
html_context = {
    "github_user": "wisrovi",
    "github_repo": "wsqlite",
    "github_version": "main",
    "doc_path": "docs",
    "canonical_url": "https://wisrovi.github.io/wsqlite/",
}

# HTML additional files
html_css_files = [
    "css/custom.css",
]

# External links
extlinks = {
    "issue": ("https://github.com/wisrovi/wsqlite/issues/%s", "Issue #%s"),
    "pr": ("https://github.com/wisrovi/wsqlite/pull/%s", "PR #%s"),
    "pypi": ("https://pypi.org/project/wsqlite/%s", "%s"),
}

# Intersphinx configuration
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pydantic": ("https://docs.pydantic.dev", None),
    "loguru": ("https://loguru.readthedocs.io/en/latest", None),
    "aiosqlite": ("https://aiosqlite.readthedocs.io/en/latest", None),
}

intersphinx_timeout = 10
intersphinx_cache_limit = 5

# Nitpicky mode
nitpicky = True
nitpicky_exclude = [
    "py:obj",
    "py:class",
]

# Source code configuration
add_function_parentheses = True

# ToDo configuration
todo_include_todos = True
todo_emit_warnings = True

# Graphviz configuration
graphviz_dot_args = [
    "-Nshape=box",
    "-Nstyle=rounded",
    "-Earrowhead=vee",
]

# Linkcheck configuration
linkcheck_timeout = 5
linkcheck_workers = 5
linkcheck_anchors = True

# Spelling configuration (optional)
# spelling_lang = "en_US"
# spelling_word_list_filename = "spelling_wordlist.txt"

# Index configuration
genindex_entries = [
    "type",
    "noindex",
]

# JSON schema configuration (optional)
# json_schemas_generate = True

# Print configuration
disable_default_color_for_warnings = [
    "api",
]

# Internationalization
language = "en"
locale_dirs = ["locale/"]
gettext_compact = False
