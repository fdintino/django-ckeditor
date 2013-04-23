from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.functional import lazy, Promise
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape
from django.utils.encoding import force_unicode
from django.utils import simplejson

from django.core.exceptions import ImproperlyConfigured
from django.forms.util import flatatt


class LazyEncoder(simplejson.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, Promise):
            lazy_unpickle, (func, args, kwargs, resultclasses) = obj.__reduce__()
            return func(*args, **kwargs)
        return obj


json_encode = LazyEncoder().encode

reverse_lazy = lazy(reverse, str)

DEFAULT_CONFIG = {
    'skin': 'django',
    'toolbar': 'Full',
    'height': 291,
    'width': 835,
    'filebrowserWindowWidth': 940,
    'filebrowserWindowHeight': 725,
    'filebrowserUploadUrl': reverse_lazy('ckeditor_upload'),
    'filebrowserBrowseUrl': reverse_lazy('ckeditor_browse'),
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
        media.add_js([media_prefix + 'ckeditor/ckeditor/ckeditor.js?timestamp=D3NG'])
        return media

    def __init__(self, config_name='default', *args, **kwargs):
        super(CKEditorWidget, self).__init__(*args, **kwargs)
        # Setup config from defaults.
        self.config = DEFAULT_CONFIG.copy()

        # Try to get valid config from settings.
        configs = getattr(settings, 'CKEDITOR_CONFIGS', None)
        if configs != None:
            if isinstance(configs, dict):
                # Make sure the config_name exists.
                if config_name in configs:
                    config = configs[config_name]
                    # Make sure the configuration is a dictionary.
                    if not isinstance(config, dict):
                        raise ImproperlyConfigured('CKEDITOR_CONFIGS["%s"] \
                                setting must be a dictionary type.' % \
                                config_name)
                    # Override defaults with settings config.
                    self.config.update(config)
                else:
                    raise ImproperlyConfigured("No configuration named '%s' \
                            found in your CKEDITOR_CONFIGS setting." % \
                            config_name)
            else:
                raise ImproperlyConfigured('CKEDITOR_CONFIGS setting must be a\
                        dictionary type.')

    def render(self, name, value, attrs={}):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        return mark_safe(render_to_string('ckeditor/widget.html', {
            'final_attrs': flatatt(final_attrs),
            'value': conditional_escape(force_unicode(value)),
            'id': final_attrs['id'],
            'config': json_encode(self.config)
            })
        )
