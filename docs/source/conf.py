from datetime import date
import os
import sys
import django

sys.path.insert(0, os.path.abspath('../../'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'snrproject.settings'
django.setup()

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
]

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

project = 'Necoma'
author = 'Wanga Evans'
release = '0.1'
copyright=f"{date.today().year}, Wanga Evans"