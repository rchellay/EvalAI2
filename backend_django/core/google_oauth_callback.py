from django.http import HttpResponseRedirect
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()

def google_callback_view(request):
    """
    Vista personalizada que se llama después del login exitoso de Google.
    Genera un JWT token y redirige al frontend con el token.
    """
    user = request.user
    
    if user.is_authenticated:
        # Generar JWT token
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        # Redirigir al frontend con el token en la URL
        if settings.DEBUG:
            redirect_url = f'http://localhost:5173/auth/callback?token={access_token}'
        else:
            redirect_url = f'https://eval-ai-2.vercel.app/auth/callback?token={access_token}'
        
        return HttpResponseRedirect(redirect_url)
    else:
        # Si no está autenticado, redirigir al login
        if settings.DEBUG:
            return HttpResponseRedirect('http://localhost:5173/')
        else:
            return HttpResponseRedirect('https://eval-ai-2.vercel.app/')
