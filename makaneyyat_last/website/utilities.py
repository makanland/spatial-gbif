from django.utils import translation

class TranslatedField(object):
    def __init__(self, en_field, ar_field):
        self.en_field = en_field
        self.ar_field = ar_field

    def __get__(self, instance, owner):
        if translation.get_language() == 'ar':
            return getattr(instance, self.ar_field)
        else:
            return getattr(instance, self.en_field)