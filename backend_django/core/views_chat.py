"""
Views para el chatbot de investigación educativa
"""
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
import logging
import re

from .models import ChatSession, ChatMessage
from .serializers_chat import ChatSessionSerializer, ChatSessionListSerializer, ChatMessageSerializer
from .services.educational_research_agent import educational_research_agent

logger = logging.getLogger(__name__)


def generate_smart_title(message_text):
    """
    Genera un título inteligente basado en el contenido del mensaje,
    omitiendo saludos genéricos y extrayendo la intención real.
    """
    # Limpiar el mensaje
    text = message_text.strip().lower()
    
    # Saludos comunes a ignorar
    greetings = [
        'hola', 'buenos días', 'buenas tardes', 'buenas noches', 
        'hey', 'hi', 'hello', 'saludos', 'qué tal', 'cómo estás',
        'buen día'
    ]
    
    # Dividir en oraciones
    sentences = re.split(r'[.!?;]\s+|\n+', text)
    
    # Buscar la primera oración que NO sea solo un saludo
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # Verificar si es solo un saludo
        words = sentence.split()
        is_greeting = all(word in greetings for word in words if word)
        
        if not is_greeting and len(sentence) > 5:
            # Capitalizar primera letra
            title = sentence[0].upper() + sentence[1:]
            # Limitar longitud
            if len(title) > 50:
                title = title[:50] + '...'
            return title
    
    # Si todo era saludos, usar el mensaje completo pero con prefijo
    original = message_text.strip()
    if len(original) > 50:
        return original[:50] + '...'
    return original if original else 'Nueva conversación'


class ChatSessionViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar sesiones de chat"""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ChatSessionListSerializer
        return ChatSessionSerializer
    
    def get_queryset(self):
        """Filtrar sesiones por usuario"""
        queryset = ChatSession.objects.filter(user=self.request.user).order_by('-updated_at')
        logger.info(f"Loading chat sessions for user {self.request.user.username}: found {queryset.count()} sessions")
        return queryset
    
    def perform_create(self, serializer):
        """Crear nueva sesión asignada al usuario actual"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """
        Enviar mensaje al agente IA
        
        POST /api/ai/chat/{chat_id}/send_message/
        Body: { "message": "¿Qué dice la evidencia sobre...?" }
        """
        try:
            chat = self.get_object()
            message_text = request.data.get('message', '').strip()
            
            if not message_text:
                return Response(
                    {'error': 'El mensaje no puede estar vacío'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Guardar mensaje del usuario
            user_message = ChatMessage.objects.create(
                chat=chat,
                sender='user',
                content=message_text
            )
            
            # Obtener historial de conversación
            chat_history = []
            previous_messages = chat.messages.order_by('timestamp')[:10]  # Últimos 10 mensajes
            for msg in previous_messages:
                chat_history.append({
                    'sender': 'assistant' if msg.sender == 'assistant' else 'user',
                    'content': msg.content
                })
            
            # Procesar pregunta con el agente IA
            logger.info(f"Processing question for chat {chat.id}: {message_text}")
            result = educational_research_agent.process_question(
                question=message_text,
                chat_history=chat_history
            )
            
            # Verificar si el modelo quiere llamar a una función
            if result.get('function_call'):
                function_name = result['function_call']['name']
                function_args = result['function_call']['arguments']
                
                logger.info(f"Function call requested: {function_name}")
                
                # Ejecutar la función
                function_result = self._execute_function(request.user, function_name, function_args)
                
                # Guardar respuesta del asistente con el resultado de la función
                assistant_message = ChatMessage.objects.create(
                    chat=chat,
                    sender='assistant',
                    content=function_result.get('message', 'Acción completada.'),
                    papers=[]
                )
            else:
                # Guardar respuesta del asistente normal
                assistant_message = ChatMessage.objects.create(
                    chat=chat,
                    sender='assistant',
                    content=result.get('response', 'Lo siento, no pude generar una respuesta.'),
                    papers=result.get('papers_used', [])
                )
            
            # Actualizar título del chat si es el primer mensaje
            if chat.message_count == 2:  # Usuario + Asistente
                # Generar título inteligente basado en contenido
                title = generate_smart_title(message_text)
                chat.title = title
                chat.save()
                logger.info(f"📝 Updated chat title to: {title}")
            
            # Serializar respuesta
            response_data = {
                'user_message': ChatMessageSerializer(user_message).data,
                'assistant_message': ChatMessageSerializer(assistant_message).data,
                'success': result.get('success', True)
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            return Response(
                {'error': f'Error al procesar el mensaje: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def start_new(self, request):
        """
        Crear nueva sesión de chat y enviar primer mensaje
        
        POST /api/ai/chat/start_new/
        Body: { "message": "Primera pregunta..." }
        """
        try:
            message_text = request.data.get('message', '').strip()
            
            if not message_text:
                return Response(
                    {'error': 'El mensaje no puede estar vacío'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Crear nueva sesión
            title = generate_smart_title(message_text)
            chat = ChatSession.objects.create(
                user=request.user,
                title=title
            )
            logger.info(f"✅ Created new chat session {chat.id} for user {request.user.username} with title: {title}")
            
            # Guardar mensaje del usuario
            user_message = ChatMessage.objects.create(
                chat=chat,
                sender='user',
                content=message_text
            )
            
            # Procesar pregunta con el agente IA (sin historial)
            logger.info(f"Starting new chat {chat.id} with question: {message_text}")
            result = educational_research_agent.process_question(
                question=message_text,
                chat_history=None
            )
            
            # Verificar si el modelo quiere llamar a una función
            if result.get('function_call'):
                function_name = result['function_call']['name']
                function_args = result['function_call']['arguments']
                
                logger.info(f"Function call requested: {function_name}")
                
                # Ejecutar la función
                function_result = self._execute_function(request.user, function_name, function_args)
                
                # Guardar respuesta del asistente con el resultado de la función
                assistant_message = ChatMessage.objects.create(
                    chat=chat,
                    sender='assistant',
                    content=function_result.get('message', 'Acción completada.'),
                    papers=[]
                )
            else:
                # Guardar respuesta del asistente normal
                assistant_message = ChatMessage.objects.create(
                    chat=chat,
                    sender='assistant',
                    content=result.get('response', 'Lo siento, no pude generar una respuesta.'),
                    papers=result.get('papers_used', [])
                )
            
            # Serializar respuesta completa
            chat_data = ChatSessionSerializer(chat).data
            
            return Response({
                'chat': chat_data,
                'success': result.get('success', True)
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error starting new chat: {e}", exc_info=True)
            return Response(
                {'error': f'Error al iniciar el chat: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _execute_function(self, user, function_name, function_args):
        """
        Ejecuta la función solicitada por el modelo
        
        Args:
            user: Usuario que hace la petición
            function_name: Nombre de la función a ejecutar
            function_args: Argumentos de la función
            
        Returns:
            Dict con el resultado de la función
        """
        from .models import Student, Group, Subject
        
        try:
            if function_name == 'create_student':
                name = function_args.get('name')
                group_id = function_args.get('group_id')
                
                if not name or not group_id:
                    return {
                        'success': False,
                        'message': 'Faltan parámetros: necesito el nombre del alumno y el ID del grupo.'
                    }
                
                try:
                    group = Group.objects.get(id=group_id, teacher=user)
                except Group.DoesNotExist:
                    return {
                        'success': False,
                        'message': f'No se encontró el grupo con ID {group_id}. ¿Cuál es el nombre del grupo correcto?'
                    }
                
                # Crear el alumno (usar grupo_principal, no group)
                student = Student.objects.create(
                    name=name,
                    grupo_principal=group
                )
                
                return {
                    'success': True,
                    'message': f'✅ Alumno "{name}" creado exitosamente en el grupo "{group.name}".',
                    'student_id': student.id
                }
            
            elif function_name == 'create_group':
                group_name = function_args.get('group_name')
                student_names = function_args.get('student_names', [])
                
                if not group_name:
                    return {
                        'success': False,
                        'message': 'Falta el nombre del grupo.'
                    }
                
                # Crear el grupo
                group = Group.objects.create(
                    name=group_name,
                    teacher=user
                )
                
                # Crear los alumnos
                students_created = []
                for student_name in student_names:
                    student = Student.objects.create(
                        name=student_name,
                        grupo_principal=group
                    )
                    students_created.append(student.name)
                
                return {
                    'success': True,
                    'message': f'✅ Grupo "{group_name}" creado con {len(students_created)} alumnos: {", ".join(students_created)}',
                    'group_id': group.id
                }
            
            elif function_name == 'create_subject':
                from datetime import time
                
                subject_name = function_args.get('subject_name')
                days = function_args.get('days', ['L'])  # Default: Lunes
                start_time_str = function_args.get('start_time', '09:00')
                end_time_str = function_args.get('end_time', '10:00')
                color = function_args.get('color', '#3B82F6')
                
                if not subject_name:
                    return {
                        'success': False,
                        'message': 'Falta el nombre de la asignatura.'
                    }
                
                # Parsear horas
                try:
                    start_hour, start_min = map(int, start_time_str.split(':'))
                    end_hour, end_min = map(int, end_time_str.split(':'))
                    start_time = time(start_hour, start_min)
                    end_time = time(end_hour, end_min)
                except:
                    start_time = time(9, 0)
                    end_time = time(10, 0)
                
                # Crear la asignatura
                subject = Subject.objects.create(
                    name=subject_name,
                    teacher=user,
                    days=days,
                    start_time=start_time,
                    end_time=end_time,
                    color=color
                )
                
                return {
                    'success': True,
                    'message': f'✅ Asignatura "{subject_name}" creada exitosamente.',
                    'subject_id': subject.id
                }
            
            elif function_name == 'create_rubric':
                from .models import Rubric, RubricCriterion, RubricLevel
                
                rubric_name = function_args.get('rubric_name')
                subject_name = function_args.get('subject_name', None)
                criteria = function_args.get('criteria', [])
                performance_levels = function_args.get('performance_levels', ['Excelente', 'Notable', 'Aprobado', 'Insuficiente'])
                
                if not rubric_name:
                    return {
                        'success': False,
                        'message': 'Falta el nombre de la rúbrica.'
                    }
                
                if not criteria:
                    return {
                        'success': False,
                        'message': 'La rúbrica necesita al menos un criterio. Por ejemplo: "Comprensión del contenido", "Presentación", etc.'
                    }
                
                # Buscar la asignatura si se proporciona
                subject = None
                if subject_name:
                    subject = Subject.objects.filter(name__icontains=subject_name, teacher=user).first()
                
                # Crear la rúbrica
                rubric = Rubric.objects.create(
                    name=rubric_name,
                    teacher=user,
                    subject=subject
                )
                
                # Crear niveles de desempeño
                levels_created = []
                for idx, level_name in enumerate(performance_levels):
                    level = RubricLevel.objects.create(
                        rubric=rubric,
                        name=level_name,
                        score=len(performance_levels) - idx  # 4, 3, 2, 1
                    )
                    levels_created.append(level)
                
                # Crear criterios
                criteria_created = []
                for criterion_text in criteria:
                    criterion = RubricCriterion.objects.create(
                        rubric=rubric,
                        description=criterion_text,
                        weight=1.0
                    )
                    criteria_created.append(criterion.description)
                
                return {
                    'success': True,
                    'message': f'✅ Rúbrica "{rubric_name}" creada con {len(criteria_created)} criterios: {", ".join(criteria_created)}',
                    'rubric_id': rubric.id,
                    'levels': [l.name for l in levels_created],
                    'criteria': criteria_created
                }
            
            else:
                return {
                    'success': False,
                    'message': f'Función desconocida: {function_name}'
                }
                
        except Exception as e:
            logger.error(f"Error executing function {function_name}: {e}", exc_info=True)
            return {
                'success': False,
                'message': f'Error al ejecutar la función: {str(e)}'
            }


@api_view(['POST'])
def test_research_search(request):
    """
    Endpoint de prueba para búsqueda de papers
    
    POST /api/ai/test-search/
    Body: { "query": "cooperative learning primary education" }
    """
    from ..services.research_search import research_search_service
    
    try:
        query = request.data.get('query', '')
        
        if not query:
            return Response(
                {'error': 'Query is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        papers = research_search_service.search_combined(query, limit=5)
        
        return Response({
            'query': query,
            'papers_found': len(papers),
            'papers': papers
        })
        
    except Exception as e:
        logger.error(f"Error in test search: {e}", exc_info=True)
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
