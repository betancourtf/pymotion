from rest_framework.authtoken.models import Token
from django.http import JsonResponse


def token_user_middleware(get_response):
    def middleware(request):
        if request.META.get('HTTP_AUTHORIZATION'):
            try:
                token = Token.objects.get(key=request.META.get('HTTP_AUTHORIZATION'))
            except Token.DoesNotExist:
                return JsonResponse({'details': "User Token Error - We couldn't validate your user"}, status=401)
            else:
                request.token_user = token.user
        return get_response(request)
    return middleware

