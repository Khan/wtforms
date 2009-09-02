"""
WTForms
=======

WTForms is a forms handling library for web applications in python. For
documentation and help please visit the `official website <http://wtforms.simplecodes.com/>`_.

The `WTForms tip <http://dev.simplecodes.com/hg/wtforms/archive/tip.zip#egg=WTForms-dev>`_
is installable via `easy_install` with ``easy_install WTForms==dev``.
"""
from wtforms.form import Form
from wtforms.fields import *
from wtforms.validators import ValidationError
from wtforms import validators, widgets

try:
    __version__ = __import__('pkg_resources').get_distribution('WTForms').version
except:
    __version__ = 'unknown'
