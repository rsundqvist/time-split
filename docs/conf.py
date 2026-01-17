"""Sphinx configuration."""

import os
from datetime import datetime, timezone

if True:  # E402 hack
    os.environ["SPHINX_BUILD"] = "true"

import shutil
from importlib import import_module, metadata

from docutils.nodes import Text, reference
from rics._internal_support import make_toc_tree_titles_shorter, myst_parser_markdown_doc_refs
from rics._internal_support.changelog import split_changelog

import time_split

myst_parser_markdown_doc_refs.patch()
make_toc_tree_titles_shorter.patch()

type_modules = ("time_split.integration.pandas",)

for tm in type_modules:
    import_module(tm)


def callback(_app, _env, node, _contnode):  # noqa
    reftarget = node.get("reftarget")

    if reftarget == "dict[str":
        # TODO(2025-01-17): Fix <unknown>:1: WARNING: py:class reference target not found: dict[str [ref.class]
        # Error on
        #   DatasetConfig.aggregations: dict[str, str] = field(default_factory)
        # Not sure what causes it. Dataclass type hints seem broken, but didn't warn before.
        raise ValueError("fix this!")

    if reftarget == "polars.dataframe.frame.DataFrame":
        # https://github.com/pola-rs/polars/issues/7027
        ans_hax = reference(
            refuri="https://docs.pola.rs/py-polars/html/reference/dataframe/index.html", reftitle=reftarget
        )
        ans_hax.children.append(Text(reftarget.rpartition(".")[-1]))
        return ans_hax

    for m in type_modules:
        if reftarget.startswith(m):
            ans_hax = reference(refuri=m + ".html#" + reftarget, reftitle=reftarget)
            ans_hax.children.append(Text(reftarget.rpartition(".")[-1]))
            return ans_hax

    return None


def setup(app):  # noqa
    app.connect("missing-reference", callback)  # Fixes linking of typevars


# -- Project information -------------------------------------------------------

# General information about the project.
_metadata = metadata.metadata(time_split.__name__)
project = _metadata["Name"]
copyright = _metadata["Author"] + f", {datetime.now(tz=timezone.utc).year}"
author = _metadata["Author"]
# The version info for the project you're documenting, acts as replacement
# for |version| and |release|, also used in various other places throughout
# the built documents.
#
# The full version, including alpha/beta/rc tags.
release = _metadata["Version"]
# The short X.Y version.
version = ".".join(release.split(".")[:2])

rics_docs = f"https://rics.readthedocs.io/en/{'latest' if 'dev' in release else 'stable'}/"
id_translation_docs = f"https://id-translation.readthedocs.io/en/{'latest' if 'dev' in release else 'stable'}/"
# -- General configuration -----------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosectionlabel",
    "sphinx_gallery.gen_gallery",
    "sphinx.ext.mathjax",
    "myst_parser",
    "sphinx_llm.txt",
]
autosummary_ignore_module_all = True
autosummary_imported_members = True
# autoclass_content = "both"  # Add __init__ doc (ie. params) to class summaries
html_show_sourcelink = False  # Remove 'view source code' from top of page (for html, not python)
autodoc_inherit_docstrings = True  # If no docstring, inherit from base class
set_type_checking_flag = True  # Enable 'expensive' imports for sphinx_autodoc_typehints
nbsphinx_allow_errors = True  # Continue through Jupyter errors
# autodoc_typehints = "description" # Sphinx-native method. Not as good as sphinx_autodoc_typehints
add_module_names = False  # Remove namespaces from class/method signatures
myst_heading_anchors = (
    3  # https://myst-parser.readthedocs.io/en/v4.0.1/syntax/optional.html#auto-generated-header-anchors
)

suppress_warnings = [
    "autosectionlabel.*",  # https://github.com/sphinx-doc/sphinx/issues/7697
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    "_build",
    "_templates",
    "Thumbs.db",
    ".DS_Store",
    "**.ipynb_checkpoints",
    # "auto_examples/*.rst",  # sphinx-gallery : This is the one we link
    "auto_examples/*.ipynb",  # sphinx-gallery : prevents duplicate references
    "auto_examples/*.py",  # sphinx-gallery : prevents duplicate references
]
shutil.rmtree("/tmp/example/", ignore_errors=True)  # noqa: 1S108

# -- Options for HTML output ---------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "pydata_sphinx_theme"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.

html_theme_options = {
    "github_url": "https://github.com/rsundqvist/time-split",
    "icon_links": [
        {"name": "PyPI", "url": "https://pypi.org/project/time-split/", "icon": "fa-solid fa-box"},
    ],
    "icon_links_label": "Quick Links",
    "use_edit_page_button": False,
    "navigation_with_keys": False,
    "show_toc_level": 1,
    "navbar_end": ["navbar-icon-links"],  # Dark mode doesn't work properly; disable it
}

# Used by pydata_sphinx_theme. Partially stolen from https://mne.tools/stable/index.html
html_context = {
    "github_user": "rsundqvist",
    "github_repo": "time-split",
    "github_version": "master",
    "display_github": True,  # Integrate GitHub
    "conf_py_path": "/docs/",  # Path in the checkout to the docs root
    "default_mode": "light",  # Dark mode doesn't work properly; disable it
    "carousel": [
        dict(
            title="Split",
            text="Main entry point function.",
            url="api/time_split.html#time_split.split",
            img="_static/logo.png",
        ),
        dict(
            title="Plot",
            text="Visualization of kept and removed folds.",
            url="api/time_split.html#time_split.plot",
            img="_images/sphx_glr_step_001.png",
        ),
        dict(
            title="User guide",
            text="Overview of relevant concepts.",
            url="guide/index.html",
            img="_static/book.png",
        ),
        dict(
            title="Integrations",
            text="Convenience functions for libraries such as <i>pandas</i> and <i>scikit-learn</i>.",
            url="api/time_split.integration.html",
            img="_static/toolbox.png",
        ),
        dict(
            title="Docker <img src= https://img.shields.io/docker/image-size/rsundqvist/time-split/latest?logo=docker&label=time-split >",
            text="Explorer application Docker image.",
            url="https://hub.docker.com/r/rsundqvist/time-split/",
            img="_static/app.jpg",
        ),
        # https://img.shields.io/docker/image-size/rsundqvist/time-split/latest?style=flat&logo=docker
        # <img src= https://img.shields.io/docker/image-size/:user/:repo/:tag >
        # dict(
        #     title="ID Translation <img src= https://img.shields.io/pypi/v/id-translation.svg >",
        #     text="Documentation for the <i>id-translation</i> package.",
        #     url=id_translation_docs,
        #     img="https://raw.githubusercontent.com/rsundqvist/id-translation/master/docs/_images/translation.png",
        # ),
        dict(
            title="RiCS <img src= https://img.shields.io/pypi/v/rics.svg >",
            text=f"Backing library. Original home of the <i>{project}</i> package.",
            url=rics_docs,
            img="https://rics.readthedocs.io/en/stable/_static/logo-text.png",
        ),
    ],
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static", "_images"]
html_css_files = ["style.css"]
html_logo = "logo.png"
html_favicon = "logo-icon.png"

# -- Nitpicky configuration ----------------------------------------------------
nitpicky = True
nitpick_ignore = [
    ("py:class", "module"),
    # Third party
    ("py:class", "Axes"),
    ("py:class", "sklearn.model_selection._split.BaseCrossValidator"),
]
nitpick_ignore_regex = []

# -- Autodoc configuration -----------------------------------------------------
autodoc_typehints = "signature"
autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "member-order": "bysource",
    "show-inheritance": True,
}

# -- Intersphinx configuration -------------------------------------------------
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pandas": ("http://pandas.pydata.org/pandas-docs/stable/", None),
    # "polars": ("https://docs.pola.rs/py-polars/html/reference/", None),  # https://github.com/pola-rs/polars/issues/7027
    "numpy": ("http://docs.scipy.org/doc/numpy/", None),
    "sqlalchemy": ("https://docs.sqlalchemy.org/en/14/", None),
    "matplotlib": ("https://matplotlib.org/stable/", None),
    "seaborn": ("https://seaborn.pydata.org/", None),
    "rics": (rics_docs, None),
}

# -- Gallery configuration -------------------------------------------------
sphinx_gallery_conf = {
    "backreferences_dir": "gen_modules/backreferences",
    "gallery_dirs": ["auto_examples"],
    "filename_pattern": "/",  # Anything in the examples dirs
    "examples_dirs": ["../examples"],
    "doc_module": ("time_split",),  # Needed for .e.g. the `.. minigallery::`-directive.
}
autosummary_generate = True

# -- Nbsphinx
nbsphinx_execute = "never"

split_changelog("changelog", "../CHANGELOG.md")
