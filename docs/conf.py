# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# Add the src directory to the Python path for autodoc
sys.path.insert(0, os.path.abspath("../src"))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "wsqlite"
copyright = "2024-2026, William Steve Rodriguez Villamizar"
author = "William Steve Rodriguez Villamizar"
author_url = "https://es.linkedin.com/in/wisrovi-rodriguez"
release = "1.2.0"
version = "1.2"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    # Markdown support
    "myst_parser",
    # Documentation generation
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    # UI enhancements
    "sphinx_copybutton",
    "sphinx.ext.todo",
]

templates_path = ["_templates"]
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "**.ipynb_checkpoints",
    "README.md",
]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]

html_title = "wsqlite Documentation"
html_short_title = "wsqlite"
html_description = (
    "SQLite ORM using Pydantic models - simple, type-safe, high-performance SQLite operations"
)

# Furo theme options
html_theme_options = {
    "sidebar_hide_name": False,
    "navigation_with_keys": True,
    "top_of_page_button": "edit",
    "left_sidebar_end": ["page-toc", "local-toc"],
    "footer_icons": [
        {
            "text": "GitHub",
            "url": "https://github.com/wisrovi/wsqlite",
            "icon": "fa-brands fa-github",
        },
        {
            "text": "PyPI",
            "url": "https://pypi.org/project/wsqlite/",
            "icon": "fa-brands fa-python",
        },
        {
            "text": "LinkedIn",
            "url": "https://es.linkedin.com/in/wisrovi-rodriguez",
            "icon": "fa-brands fa-linkedin",
        },
    ],
}

# HTML context for edit links
html_context = {
    "github_user": "wisrovi",
    "github_repo": "wsqlite",
    "github_version": "main",
    "doc_path": "docs",
}

# Additional CSS files
html_css_files = [
    "css/custom.css",
]

# -- Autodoc configuration --------------------------------------------------

autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": False,
    "show-inheritance": True,
    "inherited-members": False,
}

autodoc_type_aliases = {
    "Any": "Any",
    "BaseModel": "pydantic.BaseModel",
    "Iterator": "Iterator",
    "Callable": "Callable",
}

# -- Napoleon configuration -------------------------------------------------

napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = True

# -- Intersphinx configuration ----------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pydantic": ("https://docs.pydantic.dev/latest", None),
    "aiosqlite": ("https://aiosqlite.readthedocs.io/en/latest", None),
}

# -- Copybutton configuration ----------------------------------------------

copybutton_prompt_text = r">>> |\.\.\. |\$ "
copybutton_prompt_is_regexp = True

# -- Todo configuration ---------------------------------------------------

todo_include_todos = True

# -- Source suffix ---------------------------------------------------------

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# -- Internationalization -------------------------------------------------

language = "en"
