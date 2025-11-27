# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

from docutils import nodes
from sphinx.util.nodes import nested_parse_with_titles

import re

project = 'Nau Engine'
copyright = '2025, Nau Engine'
author = 'Nau Engine'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx_design",
    "sphinx_inline_tabs",
    "sphinx_copybutton",
]

exclude_patterns = []

language = 'ru'

html_logo = '../../../static/Logo.png'
html_favicon = '../../../static/favicon.jpg'
html_css_files = ['style.css']
html_theme = 'furo'
html_static_path = ['../../../static']
templates_path = ['_templates', '../../../templates']
toc_object_entries_show_parents = 'hide'
html_theme_options = {
    "light_css_variables": {
        "font-stack": "Coil-Regular, sans-serif",
        "font-stack--headings": "Coil-Bold, sans-serif",
        "color-brand-primary": "#FF7E29",
        "toc-title-font-size": "11px",
        "toc-font-size": "12px",
        "color-highlight-on-target": "#FFEDE0",
        "color-admonition-title--warning": "rgb(255,148,79)",
        "color-admonition-title-background--warning": "rgba(255,148,79,.2)",
        "color-admonition-title--danger": "rgb(248, 84, 123)",
        "color-admonition-title-background--danger": "rgba(248, 84, 123,.2)",
        "color-admonition-title--error": "rgb(248, 84, 123)",
        "color-admonition-title-background--error": "rgba(248, 84, 123,.2)",
        "color-admonition-title--todo": "rgb(128, 128, 128)",
        "color-admonition-title-background--todo": "rgba(128, 128, 128,.2)",
        "color-admonition-title--note": "rgb(57, 182, 252)",
        "color-admonition-title-background--note": "rgba(57, 182, 252,.2)",
        "color-sidebar-link-text--top-level": "rgba(26, 26, 26, 1)",
        "color-sidebar-brand-text": "rgba(5, 5, 5, 1)",
        "api-font-size": "100%"
    },
    "dark_css_variables": {
        "font-stack": "Coil-Regular, sans-serif",
        "font-stack--headings": "Coil-Bold, sans-serif",
        "color-brand-primary": "#FF7E29",
        "toc-title-font-size": "11px",
        "toc-font-size": "12px",
        "color-highlight-on-target": "#2B1A12",
        "color-admonition-title--warning": "rgb(255,148,79)",
        "color-admonition-title-background--warning": "rgba(255,148,79,.2)",
        "color-admonition-title--danger": "rgb(248, 84, 123)",
        "color-admonition-title-background--danger": "rgba(248, 84, 123,.2)",
        "color-admonition-title--error": "rgb(248, 84, 123)",
        "color-admonition-title-background--error": "rgba(248, 84, 123,.2)",
        "color-admonition-title--todo": "rgb(128, 128, 128)",
        "color-admonition-title-background--todo": "rgba(128, 128, 128,.2)",
        "color-admonition-title--note": "rgb(57, 182, 252)",
        "color-admonition-title-background--note": "rgba(57, 182, 252,.2)",
        "color-sidebar-link-text--top-level": "rgba(209, 210, 214, 1)",
        "color-sidebar-brand-text": "rgba(207, 208, 208, 1)",
        "sidebar-item-font-size": "14px",
        "sidebar-item-line-height": "16px",
        "api-font-size": "100%"
    },
    
}
html_css_files = ["style.css"]

maximum_signature_line_length = 60

html_title = 'Руководство пользователя'
html_short_title = "Руководство"
html_split_index = False
html_show_sourcelink = False

html_sidebars = {
    "**": [
        "sidebar/brand.html",
        "sidebar/search.html",
        "sidebar/scroll-start.html",
        "sidebar/navigation.html",
        "sidebar/scroll-end.html",
        "api_link.html"
    ]
}

api_link_prefix = '/docs/beta/api-doc/generated_content/'
# api_link_prefix = 'C:/Users/nikita.yastrebov.ext/NauDocs/build/dev/api-doc/generated_content/'

# Custom role to prepend a global link prefix to hyperlinks
def link_with_prefix_role(name, rawtext, text, lineno, inliner, options={}, content=[]):

    link_text_pattern = re.compile(r' <(?P<link_text>[\w]+)>', re.MULTILINE | re.DOTALL)
    link_text_search = re.search(link_text_pattern, text)
    link_text = text
    if (link_text_search and link_text_search.group('link_text')):
        link_text = link_text_search.group('link_text')
        text = text.partition(f' <{link_text}>')[0]
    url = api_link_prefix + text

    # Create the hyperlink node
    node = nodes.reference(rawtext, link_text, refuri=url, **options)
    return [node], []

def setup(app):
    # Register the custom role 'linkwithprefix'
    app.add_role('api', link_with_prefix_role)

    # Make sure the link prefix is passed into the document context
    app.add_config_value('link_prefix', '', 'env')