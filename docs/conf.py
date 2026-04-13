"""
Sphinx Configuration for wsqlite
"""

import os
import sys

# Add source directory to path for autodoc
sys.path.insert(0, os.path.abspath("../src"))

project = "wsqlite"
copyright = "2024, William Steve Rodriguez Villamizar"
author = "William Steve Rodriguez Villamizar"
version = "1.2.0"
release = "1.2.0"

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "show-inheritance": True,
}

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "**.ipynb"]

html_theme = "furo"
html_static_path = ["_static"]

html_title = "wsqlite Documentation"
html_short_title = "wsqlite"

html_theme_options = {
    "navigation_with_keys": True,
    "top_of_page_button": "edit",
}

html_context = {
    "github_user": "wisrovi",
    "github_repo": "wsqlite",
    "github_version": "main",
    "doc_path": "docs",
}

language = "en"
