import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import api from '../lib/axios';

// Función para generar ID único de estudiante
const generateStudentId = () => {
  const timestamp = Date.now().toString().slice(-6);
  const random = Math.floor(Math.random() * 1000).toString().padStart(3, '0');
  return `STU${timestamp}${random}`;
};

// Función para calcular edad desde fecha de nacimiento
const calculateAge = (birthDate) => {
  if (!birthDate) return '';
  const today = new Date();
  const birth = new Date(birthDate);
  let age = today.getFullYear() - birth.getFullYear();
  const monthDiff = today.getMonth() - birth.getMonth();
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
    age--;
  }
  return age;
};

// Avatares predefinidos con colores
const PRESET_AVATARS = [
  { id: 1, emoji: '👨‍🎓', color: 'from-blue-400 to-blue-600' },
  { id: 2, emoji: '👩‍🎓', color: 'from-pink-400 to-pink-600' },
  { id: 3, emoji: '🧑‍💻', color: 'from-purple-400 to-purple-600' },
  { id: 4, emoji: '👨‍🔬', color: 'from-green-400 to-green-600' },
  { id: 5, emoji: '👩‍🏫', color: 'from-orange-400 to-orange-600' },
  { id: 6, emoji: '🧑‍🎨', color: 'from-red-400 to-red-600' },
  { id: 7, emoji: '👨‍⚕️', color: 'from-teal-400 to-teal-600' },
  { id: 8, emoji: '👩‍💼', color: 'from-indigo-400 to-indigo-600' },
];

export default function StudentFormPage() {
  const navigate = useNavigate();
  const { id } = useParams();
  const isEditMode = !!id;

  const [loading, setLoading] = useState(false);
  const [showAvatarModal, setShowAvatarModal] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    birth_date: '',
    student_id: isEditMode ? '' : generateStudentId(),
    avatar_type: 'initial', // 'initial', 'emoji', 'image'
    avatar_value: '',
    avatar_image: null,
    // Contacto de emergencia (opcional)
    emergency_contact_name: '',
    emergency_contact_phone: '',
    guardian_name: '',
    guardian_email: '',
    // Datos personales (opcional)
    phone: '',
    address: '',
    city: '',
    postal_code: '',
    // Datos académicos (opcional)
    special_needs: '',
    allergies: '',
    medical_conditions: '',
    teacher_notes: '',
  });

  useEffect(() => {
    if (isEditMode) {
      loadStudentData();
    }
  }, [id]);

  const loadStudentData = async () => {
    try {
      const response = await api.get(`/students/${id}/profile`);
      const student = response.data;
      setFormData({
        username: student.username || '',
        email: student.email || '',
        birth_date: student.birth_date || '',
        student_id: student.student_id || generateStudentId(),
        avatar_type: student.avatar_type || 'initial',
        avatar_value: student.avatar_value || '',
        avatar_image: null,
        emergency_contact_name: student.emergency_contact_name || '',
        emergency_contact_phone: student.emergency_contact_phone || '',
        guardian_name: student.guardian_name || '',
        guardian_email: student.guardian_email || '',
        phone: student.phone || '',
        address: student.address || '',
        city: student.city || '',
        postal_code: student.postal_code || '',
        special_needs: student.special_needs || '',
        allergies: student.allergies || '',
        medical_conditions: student.medical_conditions || '',
        teacher_notes: student.teacher_notes || '',
      });
    } catch (error) {
      console.error('Error loading student:', error);
      toast.error('Error al cargar datos del estudiante');
    }
  };

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.size > 2 * 1024 * 1024) {
        toast.error('La imagen no debe superar los 2MB');
        return;
      }
      const reader = new FileReader();
      reader.onloadend = () => {
        setFormData({
          ...formData,
          avatar_type: 'image',
          avatar_value: reader.result,
          avatar_image: file
        });
      };
      reader.readAsDataURL(file);
    }
  };

  const selectAvatar = (avatar) => {
    setFormData({
      ...formData,
      avatar_type: 'emoji',
      avatar_value: JSON.stringify(avatar)
    });
    setShowAvatarModal(false);
  };

  const renderAvatar = () => {
    const age = calculateAge(formData.birth_date);
    
    if (formData.avatar_type === 'image' && formData.avatar_value) {
      return (
        <img 
          src={formData.avatar_value} 
          alt="Avatar" 
          className="size-32 rounded-full object-cover border-4 border-white dark:border-gray-700 shadow-lg"
        />
      );
    }
    
    if (formData.avatar_type === 'emoji' && formData.avatar_value) {
      try {
        const avatar = JSON.parse(formData.avatar_value);
        return (
          <div className={`size-32 rounded-full bg-gradient-to-br ${avatar.color} flex items-center justify-center shadow-lg border-4 border-white dark:border-gray-700`}>
            <span className="text-6xl">{avatar.emoji}</span>
          </div>
        );
      } catch (e) {
        // Fallback to initial
      }
    }
    
    // Default: Initial letter
    return (
      <div className="size-32 rounded-full bg-gradient-to-br from-primary/20 to-primary/40 flex items-center justify-center shadow-lg border-4 border-white dark:border-gray-700">
        <span className="text-5xl font-bold text-primary">
          {formData.username ? formData.username[0].toUpperCase() : '?'}
        </span>
      </div>
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (isEditMode) {
        await api.put(`/students/${id}`, formData);
        toast.success('Estudiante actualizado correctamente');
      } else {
        await api.post('/auth/register', {
          ...formData,
          password: 'temporal123' // Contraseña temporal
        });
        toast.success('Estudiante creado correctamente');
      }
      navigate('/estudiantes');
    } catch (error) {
      console.error('Error saving student:', error);
      toast.error(error.response?.data?.detail || 'Error al guardar estudiante');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background-light dark:bg-background-dark">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/estudiantes')}
            className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-primary mb-4"
          >
            <span className="material-symbols-outlined">arrow_back</span>
            <span>Volver a Estudiantes</span>
          </button>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            {isEditMode ? 'Editar Estudiante' : 'Nuevo Estudiante'}
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            {isEditMode ? 'Actualiza la información del estudiante' : 'Completa el perfil del nuevo estudiante'}
          </p>
        </div>

        {/* Main Card */}
        <div className="bg-card-light dark:bg-card-dark rounded-lg p-6 shadow-sm border border-border-light dark:border-border-dark">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Profile Section */}
            <div className="flex flex-col md:flex-row items-center gap-6 pb-6 border-b border-border-light dark:border-border-dark">
              <div className="relative group">
                {renderAvatar()}
                <div className="absolute inset-0 flex items-center justify-center bg-black/50 rounded-full opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer">
                  <button
                    type="button"
                    onClick={() => setShowAvatarModal(true)}
                    className="text-white font-medium text-sm"
                  >
                    Cambiar
                  </button>
                </div>
              </div>
              <div className="flex-grow text-center md:text-left">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                  {formData.username || 'Nuevo Estudiante'}
                </h2>
                <p className="text-muted-light dark:text-muted-dark mt-1">
                  {formData.email || 'Sin email'} | {calculateAge(formData.birth_date) ? `${calculateAge(formData.birth_date)} años` : 'Sin edad'}
                </p>
                <p className="text-muted-light dark:text-muted-dark">
                  Student ID: {formData.student_id}
                </p>
              </div>
            </div>

            {/* Form Fields */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Nombre */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Nombre Completo *
                </label>
                <input
                  type="text"
                  required
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  placeholder="Ej: Sophia Rodriguez"
                  className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-border-light dark:border-border-dark rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                />
              </div>

              {/* Email */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Email <span className="text-gray-400 text-xs">(opcional)</span>
                </label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  placeholder="sophia.rodriguez@email.com"
                  className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-border-light dark:border-border-dark rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                />
              </div>

              {/* Fecha de Nacimiento */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Fecha de Nacimiento
                </label>
                <input
                  type="date"
                  value={formData.birth_date}
                  onChange={(e) => setFormData({ ...formData, birth_date: e.target.value })}
                  max={new Date().toISOString().split('T')[0]}
                  className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-border-light dark:border-border-dark rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                />
                {formData.birth_date && (
                  <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                    Edad: {calculateAge(formData.birth_date)} años
                  </p>
                )}
              </div>

              {/* Student ID - Solo lectura */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  ID de Estudiante <span className="text-gray-400 text-xs">(generado automáticamente)</span>
                </label>
                <input
                  type="text"
                  value={formData.student_id}
                  readOnly
                  className="w-full px-4 py-2 bg-gray-100 dark:bg-gray-700 border border-border-light dark:border-border-dark rounded-lg text-gray-600 dark:text-gray-400 cursor-not-allowed"
                />
              </div>
            </div>

            {/* Sección: Contacto del Estudiante */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                <span className="material-symbols-outlined text-primary">contact_phone</span>
                Contacto del Estudiante
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Teléfono del Estudiante */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Teléfono <span className="text-gray-400 text-xs">(opcional)</span>
                  </label>
                  <input
                    type="tel"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    placeholder="+34 123 456 789"
                    className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-border-light dark:border-border-dark rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                  />
                </div>

                {/* Dirección */}
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Dirección <span className="text-gray-400 text-xs">(opcional)</span>
                  </label>
                  <input
                    type="text"
                    value={formData.address}
                    onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                    placeholder="Calle Principal, 123"
                    className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-border-light dark:border-border-dark rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                  />
                </div>

                {/* Ciudad */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Ciudad <span className="text-gray-400 text-xs">(opcional)</span>
                  </label>
                  <input
                    type="text"
                    value={formData.city}
                    onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                    placeholder="Madrid"
                    className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-border-light dark:border-border-dark rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                  />
                </div>

                {/* Código Postal */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Código Postal <span className="text-gray-400 text-xs">(opcional)</span>
                  </label>
                  <input
                    type="text"
                    value={formData.postal_code}
                    onChange={(e) => setFormData({ ...formData, postal_code: e.target.value })}
                    placeholder="28001"
                    className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-border-light dark:border-border-dark rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                  />
                </div>
              </div>
            </div>

            {/* Sección: Contacto de Emergencia */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                <span className="material-symbols-outlined text-red-500">emergency</span>
                Contacto de Emergencia
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Nombre del Contacto de Emergencia */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Nombre del Contacto <span className="text-gray-400 text-xs">(opcional)</span>
                  </label>
                  <input
                    type="text"
                    value={formData.emergency_contact_name}
                    onChange={(e) => setFormData({ ...formData, emergency_contact_name: e.target.value })}
                    placeholder="María García"
                    className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-border-light dark:border-border-dark rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                  />
                </div>

                {/* Teléfono de Emergencia */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Teléfono de Emergencia <span className="text-gray-400 text-xs">(opcional)</span>
                  </label>
                  <input
                    type="tel"
                    value={formData.emergency_contact_phone}
                    onChange={(e) => setFormData({ ...formData, emergency_contact_phone: e.target.value })}
                    placeholder="+34 123 456 789"
                    className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-border-light dark:border-border-dark rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                  />
                </div>

                {/* Nombre del Tutor/Padre/Madre */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Nombre del Tutor/Padre <span className="text-gray-400 text-xs">(opcional)</span>
                  </label>
                  <input
                    type="text"
                    value={formData.guardian_name}
                    onChange={(e) => setFormData({ ...formData, guardian_name: e.target.value })}
                    placeholder="Juan Pérez"
                    className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-border-light dark:border-border-dark rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                  />
                </div>

                {/* Email del Tutor */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Email del Tutor <span className="text-gray-400 text-xs">(opcional)</span>
                  </label>
                  <input
                    type="email"
                    value={formData.guardian_email}
                    onChange={(e) => setFormData({ ...formData, guardian_email: e.target.value })}
                    placeholder="tutor@email.com"
                    className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-border-light dark:border-border-dark rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                  />
                </div>
              </div>
            </div>

            {/* Sección: Información Médica y Académica */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                <span className="material-symbols-outlined text-blue-500">medical_information</span>
                Información Médica y Académica
              </h3>
              <div className="space-y-4">
                {/* Necesidades Especiales */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Necesidades Educativas Especiales <span className="text-gray-400 text-xs">(opcional)</span>
                  </label>
                  <textarea
                    value={formData.special_needs}
                    onChange={(e) => setFormData({ ...formData, special_needs: e.target.value })}
                    placeholder="Describe cualquier necesidad especial educativa..."
                    rows="2"
                    className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-border-light dark:border-border-dark rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent resize-none"
                  />
                </div>

                {/* Alergias */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Alergias <span className="text-gray-400 text-xs">(opcional)</span>
                  </label>
                  <input
                    type="text"
                    value={formData.allergies}
                    onChange={(e) => setFormData({ ...formData, allergies: e.target.value })}
                    placeholder="Ej: Polen, frutos secos, lactosa..."
                    className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-border-light dark:border-border-dark rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                  />
                </div>

                {/* Condiciones Médicas */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Condiciones Médicas <span className="text-gray-400 text-xs">(opcional)</span>
                  </label>
                  <textarea
                    value={formData.medical_conditions}
                    onChange={(e) => setFormData({ ...formData, medical_conditions: e.target.value })}
                    placeholder="Describe cualquier condición médica importante..."
                    rows="2"
                    className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-border-light dark:border-border-dark rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent resize-none"
                  />
                </div>

                {/* Notas del Profesor */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Notas del Profesor <span className="text-gray-400 text-xs">(opcional)</span>
                  </label>
                  <textarea
                    value={formData.teacher_notes}
                    onChange={(e) => setFormData({ ...formData, teacher_notes: e.target.value })}
                    placeholder="Observaciones, comentarios sobre el estudiante..."
                    rows="3"
                    className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-border-light dark:border-border-dark rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent resize-none"
                  />
                </div>
              </div>
            </div>

            {/* Info Box */}
            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
              <div className="flex gap-3">
                <span className="material-symbols-outlined text-blue-600 dark:text-blue-400">info</span>
                <div className="flex-1">
                  <p className="text-sm font-medium text-blue-900 dark:text-blue-200">
                    Información importante
                  </p>
                  <p className="text-sm text-blue-700 dark:text-blue-300 mt-1">
                    {isEditMode 
                      ? 'Los cambios se aplicarán inmediatamente al perfil del estudiante.'
                      : 'El estudiante recibirá una contraseña temporal para acceder al sistema.'}
                  </p>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-3 pt-6 border-t border-border-light dark:border-border-dark">
              <button
                type="button"
                onClick={() => navigate('/estudiantes')}
                className="flex items-center justify-center gap-2 px-6 py-3 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition font-medium"
              >
                <span className="material-symbols-outlined text-base">close</span>
                <span>Cancelar</span>
              </button>
              <button
                type="submit"
                disabled={loading}
                className="flex-1 flex items-center justify-center gap-2 bg-primary text-white font-semibold px-6 py-3 rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition"
              >
                <span className="material-symbols-outlined text-base">
                  {isEditMode ? 'save' : 'person_add'}
                </span>
                <span>{loading ? 'Guardando...' : (isEditMode ? 'Guardar Cambios' : 'Crear Estudiante')}</span>
              </button>
            </div>
          </form>
        </div>

        {/* Additional Info Card for Edit Mode */}
        {isEditMode && (
          <div className="mt-6 bg-card-light dark:bg-card-dark rounded-lg p-6 shadow-sm border border-border-light dark:border-border-dark">
            <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">
              Acceso Rápido
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <button
                onClick={() => navigate(`/estudiantes/${id}`)}
                className="flex items-center gap-3 p-4 bg-primary/10 dark:bg-primary/20 rounded-lg hover:bg-primary/20 dark:hover:bg-primary/30 transition"
              >
                <span className="material-symbols-outlined text-primary">person</span>
                <div className="text-left">
                  <p className="font-medium text-gray-900 dark:text-white text-sm">Ver Perfil</p>
                  <p className="text-xs text-gray-600 dark:text-gray-400">Perfil completo</p>
                </div>
              </button>

              <button
                className="flex items-center gap-3 p-4 bg-green-100 dark:bg-green-900/20 rounded-lg hover:bg-green-200 dark:hover:bg-green-900/30 transition"
              >
                <span className="material-symbols-outlined text-green-600">assignment</span>
                <div className="text-left">
                  <p className="font-medium text-gray-900 dark:text-white text-sm">Evaluaciones</p>
                  <p className="text-xs text-gray-600 dark:text-gray-400">Ver historial</p>
                </div>
              </button>

              <button
                className="flex items-center gap-3 p-4 bg-blue-100 dark:bg-blue-900/20 rounded-lg hover:bg-blue-200 dark:hover:bg-blue-900/30 transition"
              >
                <span className="material-symbols-outlined text-blue-600">event</span>
                <div className="text-left">
                  <p className="font-medium text-gray-900 dark:text-white text-sm">Asistencia</p>
                  <p className="text-xs text-gray-600 dark:text-gray-400">Registro completo</p>
                </div>
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Modal de Selección de Avatar */}
      {showAvatarModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl">
            <div className="sticky top-0 bg-white dark:bg-gray-800 border-b border-border-light dark:border-border-dark p-6 flex justify-between items-center">
              <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                Elegir Avatar
              </h3>
              <button
                onClick={() => setShowAvatarModal(false)}
                className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
              >
                <span className="material-symbols-outlined">close</span>
              </button>
            </div>

            <div className="p-6 space-y-6">
              {/* Subir Imagen */}
              <div>
                <h4 className="font-semibold text-gray-900 dark:text-white mb-3">
                  Subir Imagen
                </h4>
                <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg cursor-pointer hover:border-primary hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                  <div className="flex flex-col items-center justify-center pt-5 pb-6">
                    <span className="material-symbols-outlined text-4xl text-gray-400 mb-2">
                      cloud_upload
                    </span>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      <span className="font-semibold">Haz clic para subir</span> o arrastra una imagen
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-500">
                      PNG, JPG (máx. 2MB)
                    </p>
                  </div>
                  <input
                    type="file"
                    className="hidden"
                    accept="image/png,image/jpeg,image/jpg"
                    onChange={(e) => {
                      handleImageUpload(e);
                      setShowAvatarModal(false);
                    }}
                  />
                </label>
              </div>

              {/* Avatares Predefinidos */}
              <div>
                <h4 className="font-semibold text-gray-900 dark:text-white mb-3">
                  Avatares Predefinidos
                </h4>
                <div className="grid grid-cols-4 gap-4">
                  {PRESET_AVATARS.map((avatar) => (
                    <button
                      key={avatar.id}
                      type="button"
                      onClick={() => selectAvatar(avatar)}
                      className={`size-20 rounded-full bg-gradient-to-br ${avatar.color} flex items-center justify-center hover:scale-110 transition-transform shadow-lg hover:shadow-xl`}
                    >
                      <span className="text-4xl">{avatar.emoji}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Usar Inicial */}
              <div>
                <h4 className="font-semibold text-gray-900 dark:text-white mb-3">
                  Usar Inicial
                </h4>
                <button
                  type="button"
                  onClick={() => {
                    setFormData({
                      ...formData,
                      avatar_type: 'initial',
                      avatar_value: '',
                    });
                    setShowAvatarModal(false);
                  }}
                  className="w-full px-4 py-3 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg text-gray-900 dark:text-white font-medium transition-colors"
                >
                  Usar primera letra del nombre
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
