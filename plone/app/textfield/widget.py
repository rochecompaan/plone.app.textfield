from Acquisition import ImplicitAcquisitionWrapper

from zope.interface import implementsOnly, implementer
from zope.component import adapts, adapter

from zope.app.component.hooks import getSite

from z3c.form.interfaces import ITextAreaWidget, IFormLayer, IFieldWidget, NOVALUE
from z3c.form.browser.textarea import TextAreaWidget
from z3c.form.browser.widget import addFieldClass
from z3c.form.widget import FieldWidget
from z3c.form.converter import BaseDataConverter

from plone.app.textfield.interfaces import IRichText, IRichTextValue
from plone.app.textfield.value import RichTextValue

from plone.app.textfield.utils import getSiteEncoding, getAllowedContentTypes

class IRichTextWidget(ITextAreaWidget):
    
    def allowedMimeTypes():
        """Get allowed MIME types
        """

class RichTextWidget(TextAreaWidget):
    implementsOnly(IRichTextWidget)
    
    klass = u'richTextWidget'
    value = None

    def update(self):
        super(RichTextWidget, self).update()
        addFieldClass(self)

        # We'll wrap context in the current site *if* it's not already
        # wrapped.  This allows the template to acquire tools with
        # ``context/portal_this`` if context is not wrapped already.
        # Any attempts to satisfy the Kupu template in a less idiotic
        # way failed:
        if self.context is not None and getattr(self.context, 'aq_inner', None) is None:
            self.context = ImplicitAcquisitionWrapper(
                self.context, getSite())
    
    def extract(self, default=NOVALUE):
        raw = self.request.get(self.name, default)
        
        if raw is default:
            return default
        
        mimeType = self.request.get("%s.mimeType" % self.name, self.field.default_mime_type)
        return RichTextValue(raw=raw,
                             mimeType=mimeType,
                             outputMimeType=self.field.output_mime_type,
                             encoding=getSiteEncoding())

    def allowedMimeTypes(self):
        allowed = self.field.allowed_mime_types
        if allowed is None:
            allowed = getAllowedContentTypes()
        return list(allowed)

@adapter(IRichText, IFormLayer)
@implementer(IFieldWidget)
def RichTextFieldWidget(field, request):
    """IFieldWidget factory for RichTextWidget."""
    return FieldWidget(field, RichTextWidget(request))

class RichTextConverter(BaseDataConverter):
    """Data converter for the RichTextWidget
    """
    
    adapts(IRichText, IRichTextWidget)
    
    def toWidgetValue(self, value):
        if IRichTextValue.providedBy(value):
            return value
        elif isinstance(value, unicode):
            return self.field.fromUnicode(value)
        raise ValueError("Cannot convert %s to an IRichTextValue" % repr(value))

    def toFieldValue(self, value):
        if IRichTextValue.providedBy(value):
            return value
        elif isinstance(value, unicode):
            return self.field.fromUnicode(value)
        raise ValueError("Cannot convert %s to an IRichTextValue" % repr(value))