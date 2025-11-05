from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from django.db.models import Q
import sys
import datetime
import traceback
from .models import Student, Group, Subject
from .serializers import StudentSerializer, GroupCreateSerializer, GroupSerializer, GroupSimpleSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def debug_group_endpoint(request):
    """Debug endpoint for Group model testing"""
    try:
        from .models import Group

        # Test basic query
        groups = Group.objects.filter(teacher=request.user)
        count = groups.count()

        # Try to serialize first group if exists
        if count > 0:
            first_group = groups.first()
            serializer = GroupCreateSerializer(first_group, context={'request': request})
            data = serializer.data
            return Response({
                'status': 'success',
                'count': count,
                'first_group': data
            })
        else:
            return Response({
                'status': 'success',
                'count': 0,
                'message': 'No groups found for user'
            })

    except Exception as e:
        return Response({
            'error': str(e),
            'traceback': traceback.format_exc(),
            'error_type': type(e).__name__
        }, status=500)


class GroupHierarchyViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión jerárquica de grupos y estudiantes
    """
    permission_classes = [AllowAny]  # TEMPORARY: Remove auth to debug

    def get_serializer_class(self):
        if self.action == 'create':
            return GroupCreateSerializer
        return GroupSerializer

    def get_queryset(self):
        import logging
        logger = logging.getLogger(__name__)
        
        # TEMP FIX: Si no hay usuario autenticado, devolver todos los grupos
        if not self.request.user.is_authenticated:
            queryset = Group.objects.all()
            print(f"FORCED DEBUG: Anonymous user, returning all groups: {queryset.count()}")
            return queryset
        
        # Superusers ven todo
        if self.request.user.is_superuser:
            queryset = Group.objects.all()
            logger.info(f"GroupHierarchyViewSet - ADMINISTRATOR: returning all groups: {queryset.count()}")
        else:
            queryset = Group.objects.filter(teacher=self.request.user)
            logger.info(f"GroupHierarchyViewSet - LIST: User: {self.request.user.username} (ID: {self.request.user.id}) - returning own groups: {queryset.count()}")
            for group in queryset:
                logger.info(f"  - Group: {group.name} (ID: {group.id}) teacher: {group.teacher.username if group.teacher else 'None'}")
        return queryset

    def perform_create(self, serializer):
        # Importante: asegurar que el serializer pueda manejar el campo teacher
        import logging
        logger = logging.getLogger(__name__)
        
        # TEMP FIX: Si no hay usuario, usar el primer usuario disponible
        if not self.request.user.is_authenticated:
            from django.contrib.auth.models import User
            first_user = User.objects.first()
            print(f"FORCED DEBUG: Anonymous user creating group, using first user: {first_user.username}")
            instance = serializer.save(teacher=first_user)
        else:
            logger.info(f"GroupHierarchyViewSet - Creating group for user: {self.request.user.username} (ID: {self.request.user.id})")
            logger.info(f"GroupHierarchyViewSet - User is authenticated: {self.request.user.is_authenticated}")
            logger.info(f"GroupHierarchyViewSet - User is superuser: {self.request.user.is_superuser}")
            instance = serializer.save(teacher=self.request.user)
        
        logger.info(f"GroupHierarchyViewSet - Group created: {instance.name} (ID: {instance.id}) with teacher: {instance.teacher.username if instance.teacher else 'None'}")
        return instance
    
    @action(detail=True, methods=['get', 'post'], url_path='alumnos')
    def alumnos(self, request, pk=None):
        """
        Gestionar estudiantes de un grupo específico
        GET /api/grupos/{id}/alumnos/ - Obtener estudiantes
        POST /api/grupos/{id}/alumnos/ - Crear nuevo estudiante
        """
        # DIRECT LOGGING - NO IMPORTS
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        def direct_log(msg):
            log_msg = f"[{timestamp}] EVALAI_DEBUG: {msg}"
            print(log_msg, flush=True)
            sys.stderr.write(log_msg + "\n")
            sys.stderr.flush()
        
        direct_log(f"alumnos action called for group {pk}, method {request.method}")
        direct_log(f"User authenticated: {request.user.is_authenticated}")
        direct_log(f"User: {request.user.username if request.user.is_authenticated else 'Anonymous'}")
        
        if request.method == 'GET':
            return self.get_group_students_simple(request, pk)
        elif request.method == 'POST':
            return self.create_student_in_group_simple(request, pk)
    
    def get_group_students_simple(self, request, pk=None):
        """
        Versión simplificada para obtener estudiantes
        """
        # DIRECT LOGGING
        def direct_log(msg):
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_msg = f"[{timestamp}] EVALAI_GET: {msg}"
            print(log_msg, flush=True)
            sys.stderr.write(log_msg + "\n")
            sys.stderr.flush()
            
        direct_log(f"get_group_students_simple called for group {pk}")
        
        try:
            group = self.get_object()
            direct_log(f"Found group {group.name} (ID: {group.id})")
            
            # Solo estudiantes principales del grupo
            students = Student.objects.filter(grupo_principal=group)
            direct_log(f"Found {students.count()} students in group")
            
            # Debug: Mostrar todos los estudiantes encontrados
            for s in students:
                direct_log(f"Student found - ID: {s.id}, Name: {s.name} {s.apellidos}, Email: {s.email}")
            
            # Serializar de forma simple
            student_data = []
            for student in students:
                student_data.append({
                    'id': student.id,
                    'name': student.name,
                    'apellidos': student.apellidos,
                    'email': student.email,
                    'full_name': student.full_name,
                    'photo': student.photo,
                    'attendance_percentage': student.attendance_percentage if hasattr(student, 'attendance_percentage') else 0,
                    'created_at': student.created_at,
                    'updated_at': student.updated_at
                })
            
            direct_log(f"Serialized {len(student_data)} students")
            
            return Response({
                'status': 'success',
                'students': student_data,
                'counts': {
                    'total': len(student_data)
                }
            })
            
        except Exception as e:
            direct_log(f"ERROR in get_group_students_simple: {str(e)}")
            direct_log(f"Traceback: {traceback.format_exc()}")
            return Response(
                {'error': f'Error: {str(e)}'}, 
                status=500
            )
    
    def create_student_in_group_simple(self, request, pk=None):
        """
        Versión simplificada para crear estudiante
        """
        # DIRECT LOGGING
        def direct_log(msg):
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_msg = f"[{timestamp}] EVALAI_POST: {msg}"
            print(log_msg, flush=True)
            sys.stderr.write(log_msg + "\n")
            sys.stderr.flush()
            
        direct_log(f"create_student_in_group_simple called for group {pk}")
        
        try:
            group = self.get_object()
            direct_log(f"Found group {group.name} (ID: {group.id})")
            
            # Crear estudiante directamente sin validaciones complejas
            direct_log(f"Creating student with data - name: {request.data.get('name')}, apellidos: {request.data.get('apellidos')}, email: {request.data.get('email')}")
            
            student = Student.objects.create(
                name=request.data.get('name', ''),
                apellidos=request.data.get('apellidos', ''),
                email=request.data.get('email', ''),
                grupo_principal=group
            )
            
            direct_log(f"Student created: {student.full_name} (ID: {student.id}) in group {group.id}")
            direct_log(f"Student's grupo_principal: {student.grupo_principal.id if student.grupo_principal else None}")
            
            # Verificar que efectivamente se creó
            verify_count = Student.objects.filter(grupo_principal=group).count()
            direct_log(f"Total students in group after creation: {verify_count}")
            
            return Response({
                'status': 'success',
                'message': f'Estudiante {student.full_name} creado',
                'student': {
                    'id': student.id,
                    'name': student.name,
                    'apellidos': student.apellidos,
                    'email': student.email,
                    'full_name': student.full_name
                }
            }, status=201)
            
        except Exception as e:
            direct_log(f"ERROR in create_student_in_group_simple: {str(e)}")
            direct_log(f"Traceback: {traceback.format_exc()}")
            return Response(
                {'error': f'Error: {str(e)}'}, 
                status=500
            )
    
    @action(detail=True, methods=['post'], url_path='add_existing_alumno')
    def add_existing_student_to_group(self, request, pk=None):
        """
        Añadir estudiante existente como subgrupo
        POST /api/grupos/{id}/add_existing_alumno/
        
        Body:
        {
            "alumno_id": 42
        }
        """
        try:
            group = self.get_object()
            
            if 'alumno_id' not in request.data:
                return Response(
                    {'error': 'Campo requerido: alumno_id'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            student_id = request.data['alumno_id']
            
            try:
                student = Student.objects.get(id=student_id)
            except Student.DoesNotExist:
                return Response(
                    {'error': 'Estudiante no encontrado'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Verificar que no sea ya el grupo principal
            if student.grupo_principal == group:
                return Response(
                    {'error': 'El estudiante ya pertenece a este grupo como grupo principal'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Verificar que no esté ya como subgrupo
            if group in student.subgrupos.all():
                return Response(
                    {'error': 'El estudiante ya participa en este grupo como subgrupo'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Añadir como subgrupo
            student.subgrupos.add(group)
            
            return Response({
                'status': 'success',
                'message': f'Estudiante {student.full_name} añadido como subgrupo a {group.name}',
                'student': StudentSerializer(student, context={'request': request}).data,
                'group': {
                    'id': group.id,
                    'name': group.name,
                    'course': group.course
                }
            }, status=status.HTTP_200_OK)
            
        except Group.DoesNotExist:
            return Response(
                {'error': 'Grupo no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error al añadir estudiante: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['delete'], url_path='remove_subgrupo/(?P<student_id>[^/.]+)')
    def remove_student_from_subgrupo(self, request, pk=None, student_id=None):
        """
        Remover estudiante de subgrupo
        DELETE /api/grupos/{id}/remove_subgrupo/{student_id}/
        """
        try:
            group = self.get_object()
            
            try:
                student = Student.objects.get(id=student_id)
            except Student.DoesNotExist:
                return Response(
                    {'error': 'Estudiante no encontrado'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Verificar que esté como subgrupo
            if group not in student.subgrupos.all():
                return Response(
                    {'error': 'El estudiante no participa en este grupo como subgrupo'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Remover de subgrupos
            student.subgrupos.remove(group)
            
            return Response({
                'status': 'success',
                'message': f'Estudiante {student.full_name} removido del subgrupo {group.name}'
            }, status=status.HTTP_200_OK)
            
        except Group.DoesNotExist:
            return Response(
                {'error': 'Grupo no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error al remover estudiante: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StudentHierarchyViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión jerárquica de estudiantes
    """
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        import logging
        logger = logging.getLogger(__name__)
        # Superusers ven todo
        if self.request.user.is_superuser:
            queryset = Student.objects.all()
            logger.info(f"StudentHierarchyViewSet - ADMINISTRATOR: returning all students: {queryset.count()}")
        else:
            queryset = Student.objects.filter(
                Q(grupo_principal__teacher=self.request.user) |
                Q(subgrupos__teacher=self.request.user)
            ).distinct()
            logger.info(f"StudentHierarchyViewSet - User: {self.request.user.username} - returning own students: {queryset.count()}")
        return queryset
    
    @action(detail=False, methods=['get'], url_path='available_for_group/(?P<group_id>[^/.]+)')
    def get_available_students_for_group(self, request, group_id=None):
        """
        Obtener estudiantes disponibles para añadir a un grupo específico
        GET /api/estudiantes/available_for_group/{group_id}/
        """
        try:
            # Verificar que el grupo existe
            try:
                group = Group.objects.get(id=group_id)
                # TEMPORAL: Quitar permisos para debug
                # if not self.request.user.is_superuser and group.teacher != self.request.user:
                #     return Response(
                #         {'error': 'No tienes permisos para acceder a este grupo'},
                #         status=status.HTTP_403_FORBIDDEN
                #     )
            except Group.DoesNotExist:
                return Response(
                    {'error': 'Grupo no encontrado'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Estudiantes que NO pertenecen a este grupo (ni como principal ni como subgrupo)
            available_students = Student.objects.exclude(
                Q(grupo_principal=group) | Q(subgrupos=group)
            )
            
            # Si no es superuser, filtrar solo estudiantes de sus grupos
            if not self.request.user.is_superuser:
                available_students = available_students.filter(
                    Q(grupo_principal__teacher=self.request.user) | 
                    Q(subgrupos__teacher=self.request.user)
                ).distinct()
            
            serializer = StudentSerializer(available_students, many=True, context={'request': request})
            
            return Response({
                'status': 'success',
                'group': {
                    'id': group.id,
                    'name': group.name,
                    'course': group.course
                },
                'available_students': serializer.data,
                'count': available_students.count()
            })
            
        except Exception as e:
            return Response(
                {'error': f'Error al obtener estudiantes disponibles: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'], url_path='groups')
    def get_student_groups(self, request, pk=None):
        """
        Obtener todos los grupos donde participa un estudiante
        GET /api/estudiantes/{id}/groups/
        """
        try:
            student = self.get_object()
            
            groups_data = []
            
            # Grupo principal
            groups_data.append({
                'group': GroupSerializer(student.grupo_principal, context={'request': request}).data,
                'type': 'principal',
                'type_label': 'Grupo Principal'
            })
            
            # Subgrupos
            for subgrupo in student.subgrupos.all():
                groups_data.append({
                    'group': GroupSerializer(subgrupo, context={'request': request}).data,
                    'type': 'subgrupo',
                    'type_label': 'Subgrupo'
                })
            
            return Response({
                'status': 'success',
                'student': StudentSerializer(student, context={'request': request}).data,
                'groups': groups_data,
                'total_groups': len(groups_data)
            })
            
        except Student.DoesNotExist:
            return Response(
                {'error': 'Estudiante no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error al obtener grupos del estudiante: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
