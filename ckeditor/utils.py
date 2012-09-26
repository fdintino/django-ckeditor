from django.core.exceptions import ImproperlyConfigured


def validate_configs(configs, config_name=None):
    if configs is None:
        return

    if not isinstance(configs, dict):
        raise ImproperlyConfigured("CKEDITOR_CONFIGS setting must be a "
                                   "dictionary type.")

    # Make sure the config_name exists.
    if config_name is not None and config_name not in configs:
        raise ImproperlyConfigured(
            ("No configuration named '%s' found in your CKEDITOR_CONFIGS "
             "setting.") % config_name)

    for config_name, config in configs.iteritems():
        # Make sure the configuration is a dict
        if not isinstance(config, dict):
            raise ImproperlyConfigured(
                "CKEDITOR_CONFIGS['%s'] setting must be a dictionary type." \
                    % config_name)
