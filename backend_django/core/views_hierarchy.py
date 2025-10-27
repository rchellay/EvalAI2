from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from django.db.models import Q
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
        import traceback
        return Response({
            'error': str(e),
            'traceback': traceback.format_exc(),
            'error_type': type(e).__name__
        }, status=500)


class GroupHierarchyViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión jerárquica de grupos y estudiantes
    """
    serializer_class = GroupSimpleSerializer  # Usando serializer simplificado temporalmente
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        print(f"[DEBUG GroupHierarchyViewSet] User: {self.request.user}, is_superuser: {self.request.user.is_superuser}")
        # Superusers ven todo
        if self.request.user.is_superuser:
            queryset = Group.objects.all()
            print(f"[DEBUG GroupHierarchyViewSet] Superuser - returning all groups: {queryset.count()}")
            return queryset
        # Filtrar grupos del profesor actual
        queryset = Group.objects.filter(teacher=self.request.user)
        print(f"[DEBUG GroupHierarchyViewSet] User {self.request.user.username} - groups: {queryset.count()}")
        return queryset

    def perform_create(self, serializer):
        # Importante: asegurar que el serializer pueda manejar el campo teacher
        instance = serializer.save(teacher=self.request.user)
        print(f"[DEBUG perform_create] Group created: {instance.name} ({instance.id}) by user: {self.request.user.username}")
        return instance
    
    @action(detail=True, methods=['get'], url_path='alumnos')
    def get_group_students(self, request, pk=None):
        """
        Obtener estudiantes de un grupo específico
        GET /api/grupos/{id}/alumnos/
        """
        try:
            group = self.get_object()
            
            # Estudiantes principales del grupo
            main_students = Student.objects.filter(grupo_principal=group)
            
            # Estudiantes que participan como subgrupo
            subgrupo_students = Student.objects.filter(subgrupos=group)
            
            # Combinar ambos tipos
            all_students = main_students.union(subgrupo_students).distinct()
            
            serializer = StudentSerializer(all_students, many=True, context={'request': request})
            
            return Response({
                'status': 'success',
                'group': {
                    'id': group.id,
                    'name': group.name,
                    'course': group.course
                },
                'students': serializer.data,
                'counts': {
                    'main_students': main_students.count(),
                    'subgrupo_students': subgrupo_students.count(),
                    'total': all_students.count()
                }
            })
            
        except Group.DoesNotExist:
            return Response(
                {'error': 'Grupo no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error al obtener estudiantes: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], url_path='alumnos')
    def create_student_in_group(self, request, pk=None):
        """
        Crear nuevo estudiante dentro de un grupo específico
        POST /api/grupos/{id}/alumnos/
        
        Body:
        {
            "name": "Jesmeen",
            "apellidos": "Singh",
            "email": "jesmeen@example.com"
        }
        """
        try:
            group = self.get_object()
            
            # Validar datos requeridos
            required_fields = ['name', 'apellidos', 'email']
            for field in required_fields:
                if field not in request.data:
                    return Response(
                        {'error': f'Campo requerido: {field}'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Verificar que el email no exista
            if Student.objects.filter(email=request.data['email']).exists():
                return Response(
                    {'error': 'Ya existe un estudiante con este email'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Crear estudiante con grupo principal
            student_data = request.data.copy()
            student_data['grupo_principal'] = group.id
            
            serializer = StudentSerializer(data=student_data)
            if serializer.is_valid():
                student = serializer.save()
                
                return Response({
                    'status': 'success',
                    'message': f'Estudiante {student.full_name} creado en grupo {group.name}',
                    'student': StudentSerializer(student, context={'request': request}).data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {'error': 'Datos inválidos', 'details': serializer.errors}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Group.DoesNotExist:
            return Response(
                {'error': 'Grupo no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error al crear estudiante: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
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
        # Superusers ven todo
        if self.request.user.is_superuser:
            return Student.objects.all()
        
        # Filtrar estudiantes de grupos del profesor actual
        return Student.objects.filter(
            Q(grupo_principal__teacher=self.request.user) | 
            Q(subgrupos__teacher=self.request.user)
        ).distinct()
    
    @action(detail=False, methods=['get'], url_path='available_for_group/(?P<group_id>[^/.]+)')
    def get_available_students_for_group(self, request, group_id=None):
        """
        Obtener estudiantes disponibles para añadir a un grupo específico
        GET /api/estudiantes/available_for_group/{group_id}/
        """
        try:
            # Verificar que el grupo existe y pertenece al profesor
            try:
                group = Group.objects.get(id=group_id)
                if not self.request.user.is_superuser and group.teacher != self.request.user:
                    return Response(
                        {'error': 'No tienes permisos para acceder a este grupo'}, 
                        status=status.HTTP_403_FORBIDDEN
                    )
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
