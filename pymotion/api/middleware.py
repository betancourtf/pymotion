from rest_framework.authtoken.models import Token


def token_user_middleware(get_response):
    def middleware(request):
        if request.META.get('HTTP_AUTHORIZATION'):
            try:
                token = Token.objects.get(key=request.META.get('HTTP_AUTHORIZATION'))
            except Token.DoesNotExist:
                request.token_user = None
            else:
                request.token_user = token.user
        return get_response(request)
    return middleware

