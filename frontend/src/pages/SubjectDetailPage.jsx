// frontend/src/pages/SubjectDetailPage.jsx
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import api from '../lib/axios';

const DAYS_OF_WEEK_ES = {
  monday: 'Lunes',
  tuesday: 'Martes',
  wednesday: 'Miércoles',
  thursday: 'Jueves',
  friday: 'Viernes',
  saturday: 'Sábado',
  sunday: 'Domingo'
};

const SubjectDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [subject, setSubject] = useState(null);
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);

  useEffect(() => {
    loadSubjectData();
  }, [id]);

  const loadSubjectData = async () => {
    try {
      setLoading(true);
      
      // Cargar información básica de la asignatura
      const subjectResponse = await api.get(`/subjects/${id}/`);
      setSubject(subjectResponse.data);
      
      // Cargar grupos de la asignatura usando la nueva API
      const groupsResponse = await api.get(`/asignaturas/${id}/grupos/`);
      // Los grupos ya incluyen estudiantes a través del serializer
      const groupsWithStudents = Array.isArray(groupsResponse.data) 
        ? groupsResponse.data.map(group => ({
            ...group,
            students: Array.isArray(group.students) ? group.students : []
          }))
        : [];
      
      setGroups(groupsWithStudents);
    } catch (error) {
      console.error('Error loading subject data:', error);
      toast.error('Error al cargar la asignatura');
      navigate('/asignaturas');
    } finally {
      setLoading(false);
    }
  };

  const handleEvaluateStudent = async (student) => {
    // Navegar directamente al perfil contextual del estudiante
    navigate(`/estudiantes/${student.id}?asignatura=${id}&fecha=${selectedDate}`);
  };

  const getAllStudents = () => {
    if (!groups) return [];
    const allStudents = [];
    groups.forEach(group => {
      if (group.students && Array.isArray(group.students)) {
        group.students.forEach(student => {
          if (!allStudents.find(s => s.id === student.id)) {
            allStudents.push({ ...student, groupName: group.name });
          }
        });
      }
    });
    return allStudents;
  };

  if (loading) {
    return (
      <div className='flex items-center justify-center h-screen'>
        <div className='animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500'></div>
      </div>
    );
  }

  if (!subject) {
    return (
      <div className='p-8'>
        <p className='text-red-600'>Asignatura no encontrada</p>
      </div>
    );
  }

  const allStudents = getAllStudents();

  return (
    <div className='flex-1 p-6 overflow-y-auto bg-gray-50'>
      <div className='max-w-7xl mx-auto'>
        <div className='flex items-center justify-between mb-6'>
          <div className='flex items-center gap-4'>
            <button
              onClick={() => navigate('/')}
              className='p-2 bg-gray-200 rounded-lg transition text-gray-700'
            >
              <span className='material-symbols-outlined'>arrow_back</span>
            </button>
            <div
              className='w-12 h-12 rounded-lg flex items-center justify-center text-xl font-bold text-white'
              style={{ backgroundColor: subject.color }}
            >
              {subject.name.charAt(0).toUpperCase()}
            </div>
            <div>
              <h1 className='text-2xl font-bold text-gray-900'>{subject.name}</h1>
              <p className='text-gray-600'>
                {subject.days?.map(day => DAYS_OF_WEEK_ES[day]).join(', ')} •
                {subject.start_time?.substring(0, 5)} - {subject.end_time?.substring(0, 5)}
              </p>
            </div>
          </div>
          <div className='flex items-center gap-4'>
            <div className='text-sm'>
              <label className='block text-gray-600 mb-1'>Fecha de evaluación</label>
              <input
                type='date'
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                className='px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
              />
            </div>
          </div>
        </div>

        <div className='grid grid-cols-1 md:grid-cols-3 gap-6 mb-8'>
          <div className='bg-white p-6 rounded-lg shadow border'>
            <p className='text-gray-600 text-sm'>Grupos</p>
            <p className='text-3xl font-bold text-gray-900 mt-2'>
              {groups?.length || 0}
            </p>
          </div>
          <div className='bg-white p-6 rounded-lg shadow border'>
            <p className='text-gray-600 text-sm'>Estudiantes</p>
            <p className='text-3xl font-bold text-gray-900 mt-2'>
              {allStudents.length}
            </p>
          </div>
          <div className='bg-white p-6 rounded-lg shadow border'>
            <p className='text-gray-600 text-sm'>Evaluaciones hoy</p>
            <p className='text-3xl font-bold text-gray-900 mt-2'>
              {allStudents.filter(student =>
                student.recent_evaluations &&
                Array.isArray(student.recent_evaluations) &&
                student.recent_evaluations.some(evaluation => evaluation.date === selectedDate)
              ).length}
            </p>
          </div>
        </div>

        <div className='space-y-6'>
          {groups?.map(group => (
            <div key={group.id} className='bg-white rounded-lg shadow border'>
              <div className='p-6 border-b border-gray-200'>
                <h2 className='text-xl font-bold text-gray-900'>{group.name}</h2>
                <p className='text-gray-600'>{group.students?.length || 0} estudiantes</p>
              </div>

              <div className='p-6'>
                {group.students && Array.isArray(group.students) && group.students.length > 0 ? (
                  <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4'>
                    {group.students.map(student => {
                      const todayEvaluation = student.recent_evaluations?.find(
                        evaluation => evaluation.date === selectedDate && evaluation.subject === parseInt(id)
                      );

                      return (
                        <div key={student.id} className='border border-gray-200 rounded-lg p-4'>
                          <div className='flex items-center justify-between mb-3'>
                            <div>
                              <h3 className='font-semibold text-gray-900'>{student.name}</h3>
                              <p className='text-sm text-gray-600'>{student.email}</p>
                            </div>
                            {todayEvaluation && (
                              <div className='text-right'>
                                <div className='text-lg font-bold text-blue-600'>
                                  {todayEvaluation.score}/10
                                </div>
                                <div className='text-xs text-gray-500'>Evaluado</div>
                              </div>
                            )}
                          </div>

                          <button
                            onClick={() => handleEvaluateStudent(student)}
                            className='w-full px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition flex items-center justify-center gap-2'
                          >
                            <span className='material-symbols-outlined text-sm'>person</span>
                            {todayEvaluation ? 'Ver Evaluación' : 'Evaluar Estudiante'}
                          </button>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <p className='text-gray-500 text-center py-8'>No hay estudiantes en este grupo</p>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default SubjectDetailPage;
