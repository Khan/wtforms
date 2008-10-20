"""
    test_fields
    ~~~~~~~~~~~
    
    Unittests for bundled fields.
    
    :copyright: 2007-2008 by James Crasta, Thomas Johansson.
    :license: MIT, see LICENSE.txt for details.
"""

from py.test import raises
from wtforms.fields import *
from wtforms.fields import Label
from wtforms.form import Form

class DummyPostData(dict):
    def getlist(self, key):
        return self[key]

class AttrDict(dict):
    def __getattr__(self, attr):
        return self[attr]

def test_Label():
    expected = u'''<label for="test">Caption</label>'''
    label = Label('test', u'Caption')
    assert label() == expected
    assert str(label) == expected
    assert unicode(label) == expected
    assert label("hello") == u'''<label for="test">hello</label>''' 

def test_SelectField():
    class F(Form):
        a = SelectField(choices=[('a', 'hello'), ('b','bye')], default='a')
        b = SelectField(choices=[(1, "Item 1"), (2, "Item 2")], checker=int)
    form = F()
    assert form.a.data == u'a'
    assert form.b.data == None
    assert form.validate() == False
    assert form.a() == u'''<select id="a" name="a"><option selected="selected" value="a">hello</option><option value="b">bye</option></select>'''
    assert form.b() == u'''<select id="b" name="b"><option value="1">Item 1</option><option value="2">Item 2</option></select>'''
    form = F(DummyPostData(b=u'2'))
    assert form.b.data == 2
    assert form.validate() == True
    form = F(obj=AttrDict(b=AttrDict(id=1)))
    assert form.b.data == 1
    assert form.validate() == True
    form.b.choices = [(3, 'false')]
    assert form.validate() == False

def test_SelectMultipleField():
    pass # TODO

def test_TextField():
    class F(Form):
        a = TextField()
    form = F()
    assert form.a.data == None
    assert form.a() == u'''<input id="a" name="a" type="text" value="" />'''
    form = F(DummyPostData(a=['hello']))
    assert form.a.data == u'hello'
    assert form.a() == u'''<input id="a" name="a" type="text" value="hello" />'''

def test_HiddenField():
    class F(Form):
        a = HiddenField(default="LE DEFAULT")
    form = F()
    assert form.a() == u'''<input id="a" name="a" type="hidden" value="LE DEFAULT" />'''

def test_TextAreaField():
    class F(Form):
        a = TextAreaField(default="LE DEFAULT")
    form = F()
    assert form.a() == u'''<textarea id="a" name="a">LE DEFAULT</textarea>'''

def test_PasswordField():
    class F(Form):
        a = PasswordField(default="LE DEFAULT")
    form = F()
    assert form.a() == u'''<input id="a" name="a" type="password" value="LE DEFAULT" />'''

def test_FileField():
    class F(Form):
        a = FileField(default="LE DEFAULT")
    form = F()
    assert form.a() == u'''<input id="a" name="a" type="file" value="LE DEFAULT" />'''

def test_IntegerField():
    class F(Form):
        a = IntegerField()
        b = IntegerField()
    form = F(DummyPostData(a=['v'], b=['-15']))
    assert form.a.data == None
    assert form.a() == u'''<input id="a" name="a" type="text" value="0" />'''
    assert form.b.data == -15
    assert form.b() == u'''<input id="b" name="b" type="text" value="-15" />'''

def test_BooleanField():
    class BoringForm(Form):
        bool1  = BooleanField()
        bool2  = BooleanField(default=True)
    obj = AttrDict(bool1=None, bool2=True)
    # Test with no post data to make sure defaults work
    form = BoringForm()
    assert form.bool1.raw_data == None
    assert form.bool1.data == False
    assert form.bool2.data == True

    # Test with one field set to make sure behaviour is correct
    form = BoringForm(DummyPostData({'bool1': [u'a']}))
    assert form.bool1.raw_data == u'a'
    assert form.bool1.data == True

    # Test with model data as well.
    form = BoringForm(obj=obj)
    assert form.bool1.data == False
    assert form.bool1.raw_data == None
    assert form.bool2.data == True

    # Test with both.
    form = BoringForm(DummyPostData({'bool1': [u'y']}), obj=obj)
    assert form.bool1.data == True
    assert form.bool2.data == False

def test_DateTimeField():
    pass # TODO

def test_SubmitField():
    pass # TODO
