from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from google.oauth2 import id_token
from google.auth.transport import requests
import os
import json

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Login endpoint"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'detail': 'Username and password required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(username=username, password=password)
    
    if user is None:
        return Response(
            {'detail': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'access_token': str(refresh.access_token),
        'refresh_token': str(refresh),
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        }
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """Register endpoint"""
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not all([username, email, password]):
        return Response(
            {'detail': 'All fields required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if User.objects.filter(username=username).exists():
        return Response(
            {'detail': 'Username already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )
    
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'access_token': str(refresh.access_token),
        'refresh_token': str(refresh),
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
def google_login_view(request):
    """Google OAuth login"""
    id_token_str = request.data.get('id_token')
    if not id_token_str:
        return Response({'error': 'ID token is required'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        idinfo = id_token.verify_oauth2_token(id_token_str, requests.Request(), client_id)
        email = idinfo['email']
        name = idinfo.get('name', '')
        user, created = User.objects.get_or_create(email=email, defaults={'username': email.split('@')[0], 'first_name': name})
        refresh = RefreshToken.for_user(user)
        return Response({
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            }
        })
    except ValueError:
        return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
@permission_classes([AllowAny])
def ping_view(request):
    """Health check"""
    return Response({'message': 'pong', 'status': 'ok'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    """Get current user info"""
    user = request.user
    profile = user.profile if hasattr(user, 'profile') else None
    
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'display_name': profile.display_name if profile else user.username,
        'avatar_url': profile.avatar.url if profile and profile.avatar else None,
        'first_name': user.first_name,
        'last_name': user.last_name,
    })

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def user_settings_view(request):
    """Get or update user settings"""
    user = request.user
    
    if request.method == 'GET':
        profile = user.profile if hasattr(user, 'profile') else None
        settings_data = json.loads(profile.settings) if profile and profile.settings else {}
        
        return Response({
            'displayName': profile.display_name if profile else user.username,
            'email': user.email,
            'centro': settings_data.get('centro', ''),
            'autoLogout': settings_data.get('autoLogout', '30'),
            'añoAcademico': settings_data.get('añoAcademico', '2024-2025'),
            'nivelEducativo': settings_data.get('nivelEducativo', 'Primaria'),
            'notifInApp': settings_data.get('notifInApp', {
                'evaluaciones': True,
                'informes': True,
                'asistencia': True,
                'grupos': True
            }),
            'notifEmail': settings_data.get('notifEmail', True),
            'recordatorios': settings_data.get('recordatorios', '15'),
            'isAdmin': user.is_staff,
        })
    
    elif request.method == 'POST':
        profile = user.profile if hasattr(user, 'profile') else None
        if not profile:
            from .models import UserProfile
            profile = UserProfile.objects.create(user=user)
        
        # Actualizar campos del perfil
        if 'displayName' in request.data:
            profile.display_name = request.data['displayName']
        
        if 'email' in request.data:
            user.email = request.data['email']
            user.save()
        
        # Guardar settings como JSON
        settings_data = {
            'centro': request.data.get('centro', ''),
            'autoLogout': request.data.get('autoLogout', '30'),
            'añoAcademico': request.data.get('añoAcademico', '2024-2025'),
            'nivelEducativo': request.data.get('nivelEducativo', 'Primaria'),
            'notifInApp': request.data.get('notifInApp', {}),
            'notifEmail': request.data.get('notifEmail', True),
            'recordatorios': request.data.get('recordatorios', '15'),
        }
        
        profile.settings = json.dumps(settings_data)
        profile.save()
        
        return Response({'message': 'Settings updated successfully'})
