from django.http import HttpResponse
import base64

def basic_auth_middleware(get_response):
    def middleware(request):
        if request.path.startswith('/dashboard/'):
            auth = request.META.get('HTTP_AUTHORIZATION')
            if auth:
                method, credentials = auth.split(' ', 1)
                username, password = base64.b64decode(credentials).decode('utf-8').split(':', 1)
                if username == 'client' and password == 'secret':
                    return get_response(request)
            response = HttpResponse("Unauthorized", status=401)
            response['WWW-Authenticate'] = 'Basic realm="Dashboard"'
            return response
        return get_response(request)
    return middleware
