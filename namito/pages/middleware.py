from django.utils.translation import activate
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

class LanguageMiddleware(MiddlewareMixin):
    def process_request(self, request):
        language = request.META.get('HTTP_ACCEPT_LANGUAGE')
        if language:
            activate(language)
        else:
            activate(settings.LANGUAGE_CODE)
