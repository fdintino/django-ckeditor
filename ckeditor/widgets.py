from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.forms.util import flatatt
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape
from django.utils.encoding import force_unicode
from django.utils import simplejson

from .utils import validate_configs


json_encode = simplejson.JSONEncoder().encode

DEFAULT_CONFIG = {
    'skin': 'django',
    'toolbar': 'Full',
    'height': 291,
    'width': 835,
    'filebrowserWindowWidth': 940,
    'filebrowserWindowHeight': 725,
}


class CKEditorWidget(forms.Textarea):
    """
    Widget providing CKEditor for Rich Text Editing.
    Supports direct image uploads and embed.
    """

    @property
    def media(self):
        media_prefix = getattr(settings, 'CKEDITOR_MEDIA_PREFIX', settings.STATIC_URL)
        if len(media_prefix) and media_prefix[-1] != '/':
            media_prefix += '/'

        media = super(CKEditorWidget, self).media
        media.add_js([
            media_prefix + 'ckeditor/ckeditor/ckeditor.js?timestamp=C8Q2',
            reverse('ckeditor.views.configs'),
        ])
        return media

    def __init__(self, config_name='default', *args, **kwargs):
        super(CKEditorWidget, self).__init__(*args, **kwargs)
        # Setup config from defaults.
        self.config = DEFAULT_CONFIG.copy()
        self.config_name = config_name

        # Try to get valid config from settings.
        configs = getattr(settings, 'CKEDITOR_CONFIGS', None)
        if configs is not None:
            validate_configs(configs, config_name)
            self.config.update(configs[config_name])

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''

        if attrs is None:
            attrs = {}

        attrs.update({
            'data-config-name': self.config_name,
            'class': 'item-richtext djckeditor-textarea',
        })

        final_attrs = self.build_attrs(attrs, name=name)
        self.config['filebrowserUploadUrl'] = reverse('ckeditor_upload')
        self.config['filebrowserBrowseUrl'] = reverse('ckeditor_browse')
        return mark_safe(render_to_string('ckeditor/widget.html', {
            'final_attrs': flatatt(final_attrs),
            'config_name': self.config_name,
            'value': conditional_escape(force_unicode(value)),
            'id': final_attrs['id'],
            'config': json_encode(self.config)
            })
        )
