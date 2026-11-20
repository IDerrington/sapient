# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'SAPIENT Sensor'
copyright = '2026, Iain Derrington'
author = 'Iain Derrington'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
]

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_theme_options = {
    'light_css_variables': {
        'color-brand-primary': '#0f665e',
        'color-brand-content': '#0f665e',
    },
    'dark_css_variables': {
        'color-brand-primary': '#73d8c5',
        'color-brand-content': '#73d8c5',
    },
}
html_static_path = ['_static']
