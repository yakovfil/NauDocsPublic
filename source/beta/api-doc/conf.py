# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Nau Engine'
copyright = '2025, Nau Engine'
author = 'Nau Engine'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [ 'breathe']


exclude_patterns = []

language = 'en'

html_logo = '../../../static/Logo.png'
html_favicon = '../../../static/favicon.jpg'
html_css_files = ['style.css']
html_theme = 'furo'
html_static_path = ['_static', '../../../static']
templates_path = ['_templates', '../../../templates']
globaltoc_maxdepth = 2
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
        "color-sidebar-brand-text": "rgba(5, 5, 5, 1)"
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
    },
    
}
breathe_projects = {"NauEngine" : "xml"}
breathe_default_project = "NauEngine"
breathe_default_members = ('members', 'protected-members', 'private-members', 'undoc-members')

html_title = 'API Reference'
html_short_title = "NAU API"
html_split_index = False
html_show_sourcelink = False

html_sidebars = {
    "**": [
        "sidebar/brand.html",
        "sidebar/search.html",
        "sidebar/scroll-start.html",
        "sidebar/navigation.html",
        "sidebar/scroll-end.html",
        "user_link.html"
    ]
}