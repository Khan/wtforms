"""
    wtforms.form
    ~~~~~~~~~~~~
    
    TODO
    
    :copyright: 2007 by James Crasta, Thomas Johansson.
    :license: MIT, see LICENSE.txt for details.
"""
from wtforms.validators import ValidationError

class Form(object):
    def __init__(self, formdata=None, model=None, prefix='', idprefix='', **kwargs):
        if prefix:
            prefix += '_'
        self._idprefix = idprefix

        # populate data from form and optional instance and defaults
        self.errors = {}
        self._fields = {}
        in_form = bool(formdata)
        for name in dir(self.__class__):
            f = getattr(self.__class__, name, None)
            if name.startswith('_') or not getattr(f, '_formfield', False):
                continue

            form_name = prefix + name

            self._fields[name] = field = f(name=form_name, form=self)
            setattr(self, name, field)

            if name in kwargs:
                field.data = kwargs[name]
            if hasattr(model, name):
                field.process_modeldata(getattr(model, name), in_form)
            if in_form and form_name in formdata:
                field.process_formdata(formdata.getlist(form_name))
            
    def validate(self):
        success = True
        for name, field in self._fields.iteritems():
            field.errors = []
            validators = list(field.validators)
            validators.append(field._validate)
            inline_validator = getattr(self.__class__, '_validate_%s' % name, None)
            if inline_validator is not None:
                validators.append(inline_validator)
            for validator in validators:
                try:
                    validator(self, field)
                except ValidationError, e:
                    field.errors.append(e.message)
            if field.errors:
                success = False
                self.errors[name] = field.errors
        return success

    def _get_data(self):
        data = {}
        for name, val in self._fields.iteritems():
            data[name] = val.data
        return data
    data = property(_get_data)

    def auto_populate(self, model):
        """
        Automatically copy our converted form values into the model object.

        This can be very dangerous if not used properly, so make sure to only use
        this in forms with proper validators and the right attributes.
        """
        for name, val in self._fields.iteritems():
            setattr(model, name, val.data)
