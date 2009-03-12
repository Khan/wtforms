"""
    wtforms.widgets
    ~~~~~~~~~~~~~~~
    
    The WTForms widget system.
    
    :copyright: 2009 by James Crasta, Thomas Johansson.
    :license: MIT, see LICENSE.txt for details.
"""
from cgi import escape

__all__ = (
    'CheckboxInput', 'FileInput', 'HiddenInput', 'ListWidget', 'PasswordInput',
    'RadioInput', 'Select', 'SubmitInput', 'TextArea', 'TextInput',
)

def html_params(**kwargs):
    """
    Generate HTML parameters for keywords
    """
    params = []
    keys = kwargs.keys()
    keys.sort()
    for k in keys:
        v = escape(unicode(kwargs[k]), quote=True)
        if k in ('class_', 'class__'):
            k = k[:-1]
        k = unicode(k)
        params.append(u'%s="%s"' % (k, v))
    return u' '.join(params)

class Widget(object):
    """
    Base class for all WTForms widgets.
    """
    def render(self, field, **kwargs):
        """
        Renders the widget. All widgets must implement this.
        
        `field`
            The field to render.
        `**kwargs`
            Any parameters used for rendering. Typically used to override or
            pass extra html attributes.
        """
        raise NotImplementedError()

class ListWidget(Widget):
    """
    Renders a list of fields as a `ul` or `ol` list.

    This is used for fields which encapsulate many inner fields as subfields.
    The widget will try to iterate the field to get access to the subfields and
    call them to render them.

    If `prefix_label` is set, the subfield's label is printed before the field,
    otherwise afterwards. The latter is useful for iterating radios or
    checkboxes.
    """
    def __init__(self, html_tag='ul', prefix_label=True):
        assert html_tag in ('ol', 'ul')
        self.html_tag = html_tag
        self.prefix_label = prefix_label

    def render(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        html = [u'<%s %s>' % (self.html_tag, html_params(**kwargs))]
        for subfield in field:
            if self.prefix_label:
                html.append(u'<li>%s: %s</li>' % (subfield.label, subfield()))
            else:
                html.append(u'<li>%s %s</li>' % (subfield(), subfield.label))
        html.append(u'</%s>' % self.html_tag)
        return u''.join(html)

class Input(Widget):
    """
    Render a basic ``<input>`` field.

    This is used as the basis for most of the other input fields.

    By default, the `_value()` method will be called upon the associated field
    to provide the ``value=`` HTML attribute.
    """
    def __init__(self, input_type=None):
        if input_type is not None:
            self.input_type = input_type

    def render(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', self.input_type)
        if 'value' not in kwargs:
            kwargs['value'] = field._value()
        return u'<input %s />' % html_params(name=field.name, **kwargs)

class TextInput(Input):
    """
    Render a single-line text input.
    """
    input_type = 'text'
    
class PasswordInput(Input):
    """
    Render a password input.

    For security purposes, this field will not reproduce the value on a form
    submit by default. To have the value filled in, set `hide_value` to
    `False`.
    """
    input_type = 'password'

    def __init__(self, hide_value=True):
        self.hide_value = hide_value

    def render(self, field, **kwargs): 
        if self.hide_value:
            kwargs['value'] = ''
        return super(PasswordInput, self).render(field, **kwargs)

class HiddenInput(Input):
    """
    Render a hidden input.
    """
    input_type = 'hidden'

class CheckboxInput(Input):
    """
    Render a checkbox.
    
    The ``value=`` HTML attribute by default is 'y' unless otherwise specified
    by `value=` to render. The ``checked`` HTML attribute is set if the field's
    data is a non-false value.
    """
    input_type = 'checkbox'

    def render(self, field, **kwargs): 
        kwargs.setdefault('value', u'y')
        if field.data:
            kwargs['checked'] = u'checked'
        return super(CheckboxInput, self).render(field, **kwargs)

class RadioInput(Input):
    """
    Render a single radio button.

    This field is most commonly used in conjunction with ListWidget or some
    other listing, as singular radio buttons are not very useful.
    """
    input_type = 'radio'

    def render(self, field, **kwargs):
        if field.checked:
            kwargs['checked'] = u'checked'
        return super(RadioInput, self).render(field, value=field.data, **kwargs)
        
class FileInput(Input):
    """
    Renders a file input chooser field.
    """
    input_type = 'file'

class SubmitInput(Input):
    """
    Renders a submit button.

    The field's label is used as the text of the submit button instead of the
    data on the field.
    """
    input_type = 'submit'

    def render(self, field, **kwargs): 
        kwargs.setdefault('value', field.label.text)
        return super(SubmitInput, self).render(field, **kwargs)

class TextArea(Widget):
    """
    Renders a multi-line text area.

    `rows` and `cols` ought to be passed as keyword args when rendering.
    """
    def render(self, field, **kwargs): 
        kwargs.setdefault('id', field.id)
        return u'<textarea %s>%s</textarea>' % (html_params(name=field.name, **kwargs), escape(unicode(field._value())))

class Select(Widget):
    """
    Renders a select field.

    If `multiple` is True, then the `size` property should be specified on
    rendering to make the field useful.

    The field must provide an `iter_choices()` method which the widget will
    call on rendering; this method must yield tuples of 
    `(value, label, selected)`.
    """
    def __init__(self, multiple=False):
        self.multiple = multiple
        
    def render(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        if self.multiple:
            kwargs['multiple'] = 'multiple'
        html = [u'<select %s>' % html_params(name=field.name, **kwargs)]
        for val, label, selected in field.iter_choices():
            options = {'value': val}
            if selected:
                options['selected'] = u'selected'
            html.append(u'<option %s>%s</option>' % (html_params(**options), escape(unicode(label))))
        html.append(u'</select>')
        return u''.join(html)

class FormTable(Widget):
    """
    Render a FormField as a set of table rows with th/td pairs.

    If `with_table_tag` is True, then an enclosing <table> is placed around the
    rows.
    """
    def __init__(self, with_table_tag=True):
        self.with_table_tag = with_table_tag

    def render(self, field, **kwargs):
        html = []
        if self.with_table_tag:
            html.append(u'<table %s>' % html_params(**kwargs))
        for subfield in field.form:
            html.append(u'<tr><th>%s<th><td>%s</td></tr>' % (unicode(subfield.label), unicode(subfield)))
        if self.with_table_tag:
            html.append(u'</table>')
        return u''.join(html)
