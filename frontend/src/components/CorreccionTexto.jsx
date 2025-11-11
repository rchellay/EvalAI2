import React, { useState, useRef, useEffect } from 'react';
import { CheckCircle, AlertCircle, Loader2, BookOpen, BarChart3, User, Save } from 'lucide-react';
import api from '../lib/axios';
import { toast } from 'react-hot-toast';

const CorreccionTexto = ({ onCorreccionCompleta }) => {
  const [texto, setTexto] = useState('');
  const [correccion, setCorreccion] = useState(null);
  const [estadisticas, setEstadisticas] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [mostrarSugerencias, setMostrarSugerencias] = useState({});
  const [idioma, setIdioma] = useState(''); // Idioma seleccionado (obligatorio)
  
  // Estados para vincular con alumno
  const [estudiantes, setEstudiantes] = useState([]);
  const [estudianteSeleccionado, setEstudianteSeleccionado] = useState(null);
  const [asignaturaSeleccionada, setAsignaturaSeleccionada] = useState(null);
  const [asignaturas, setAsignaturas] = useState([]);
  const [tituloCorreccion, setTituloCorreccion] = useState('');
  const [comentarioProfesor, setComentarioProfesor] = useState('');
  const [guardandoEvidencia, setGuardandoEvidencia] = useState(false);
  
  const textareaRef = useRef(null);

  // Cargar estudiantes y asignaturas al montar el componente
  useEffect(() => {
    cargarEstudiantes();
    cargarAsignaturas();
  }, []);

  const cargarEstudiantes = async () => {
    try {
      const response = await api.get('/students/');
      // Manejar respuesta paginada de DRF
      const data = response.data.results || response.data;
      if (data && Array.isArray(data)) {
        setEstudiantes(data);
      } else if (Array.isArray(response.data)) {
        setEstudiantes(response.data);
      } else {
        console.warn('Respuesta de estudiantes no es un array:', response.data);
        setEstudiantes([]);
      }
    } catch (err) {
      console.error('Error cargando estudiantes:', err);
      setEstudiantes([]);
      toast.error('Error al cargar la lista de estudiantes');
    }
  };

  const cargarAsignaturas = async () => {
    try {
      const response = await api.get('/subjects/');
      // Manejar respuesta paginada de DRF
      const data = response.data.results || response.data;
      if (data && Array.isArray(data)) {
        setAsignaturas(data);
      } else if (Array.isArray(response.data)) {
        setAsignaturas(response.data);
      } else {
        console.warn('Respuesta de asignaturas no es un array:', response.data);
        setAsignaturas([]);
      }
    } catch (err) {
      console.error('Error cargando asignaturas:', err);
      setAsignaturas([]);
      toast.error('Error al cargar la lista de asignaturas');
    }
  };

  const corregirTexto = async () => {
    if (!texto.trim()) {
      setError('Por favor, escribe algún texto para corregir');
      return;
    }

    if (!idioma) {
      setError('Por favor, selecciona el idioma del texto antes de corregir');
      toast.error('Debes seleccionar un idioma');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await api.post('/correccion/texto/', {
        texto: texto,
        idioma: idioma
      });

      setCorreccion(response.data.correccion);
      setEstadisticas(response.data.estadisticas);
      
      if (onCorreccionCompleta) {
        onCorreccionCompleta(response.data);
      }
    } catch (err) {
      setError('Error al corregir el texto. Inténtalo de nuevo.');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const obtenerEstadisticas = async () => {
    if (!texto.trim()) return;

    try {
      const response = await api.get('/correccion/estadisticas/', {
        params: { texto: texto }
      });
      setEstadisticas(response.data.estadisticas);
    } catch (err) {
      console.error('Error obteniendo estadísticas:', err);
    }
  };

  // Obtener estadísticas automáticamente cuando cambia el texto
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      obtenerEstadisticas();
    }, 1000);

    return () => clearTimeout(timeoutId);
  }, [texto]);

  const renderizarTextoConErrores = () => {
    if (!correccion || !correccion.matches) return texto;

    const elementos = [];
    let ultimoIndice = 0;

    // Ordenar errores por posición
    const erroresOrdenados = [...correccion.matches].sort((a, b) => a.offset - b.offset);

    erroresOrdenados.forEach((error, index) => {
      const inicio = error.offset;
      const fin = error.offset + error.length;
      
      // Agregar texto antes del error
      if (inicio > ultimoIndice) {
        elementos.push(
          <span key={`texto-${index}`} className="text-gray-900">
            {texto.substring(ultimoIndice, inicio)}
          </span>
        );
      }

      // Agregar el error marcado
      const claseSeveridad = {
        'alta': 'bg-red-200 border-red-400 text-red-900',
        'media': 'bg-yellow-200 border-yellow-400 text-yellow-900',
        'baja': 'bg-blue-200 border-blue-400 text-blue-900'
      }[error.severity] || 'bg-gray-200 border-gray-400 text-gray-900';

      elementos.push(
        <span
          key={`error-${index}`}
          className={`relative inline-block px-1 py-0.5 rounded border-b-2 cursor-pointer ${claseSeveridad}`}
          onClick={() => setMostrarSugerencias({ [inicio]: !mostrarSugerencias[inicio] })}
          title={`${error.message} - Click para ver sugerencias`}
        >
          {texto.substring(inicio, fin)}
          {mostrarSugerencias[inicio] && (
            <div className="absolute top-full left-0 z-50 mt-1 p-3 bg-white border border-gray-300 rounded-lg shadow-lg min-w-64">
              <div className="text-sm font-medium text-gray-900 mb-2">
                {error.short_message || error.message}
              </div>
              {error.suggestions && error.suggestions.length > 0 && (
                <div className="mb-2">
                  <div className="text-xs text-gray-600 mb-1">Sugerencias:</div>
                  {error.suggestions.map((sugerencia, idx) => (
                    <button
                      key={idx}
                      className="block w-full text-left px-2 py-1 text-sm bg-blue-50 hover:bg-blue-100 rounded mb-1"
                      onClick={() => aplicarSugerencia(inicio, fin, sugerencia.value)}
                    >
                      {sugerencia.value}
                    </button>
                  ))}
                </div>
              )}
              <div className="text-xs text-gray-500">
                Tipo: {error.rule_category || 'General'}
              </div>
            </div>
          )}
        </span>
      );

      ultimoIndice = fin;
    });

    // Agregar texto restante
    if (ultimoIndice < texto.length) {
      elementos.push(
        <span key="texto-final" className="text-gray-900">
          {texto.substring(ultimoIndice)}
        </span>
      );
    }

    return elementos;
  };

  const aplicarSugerencia = (inicio, fin, sugerencia) => {
    const nuevoTexto = texto.substring(0, inicio) + sugerencia + texto.substring(fin);
    setTexto(nuevoTexto);
    setMostrarSugerencias({});
  };

  const generarTextoCorregido = () => {
    if (!correccion || !correccion.matches || correccion.matches.length === 0) {
      return texto;
    }

    // Ordenar errores por posición (de atrás hacia adelante para no alterar los índices)
    const erroresOrdenados = [...correccion.matches].sort((a, b) => b.offset - a.offset);

    let textoCorregido = texto;

    // Aplicar todas las correcciones (primera sugerencia de cada error)
    erroresOrdenados.forEach((error) => {
      if (error.suggestions && error.suggestions.length > 0) {
        const inicio = error.offset;
        const fin = error.offset + error.length;
        const sugerencia = error.suggestions[0].value;

        textoCorregido = textoCorregido.substring(0, inicio) + sugerencia + textoCorregido.substring(fin);
      }
    });

    return textoCorregido;
  };

  const aplicarTodasLasCorrecciones = () => {
    const textoCorregido = generarTextoCorregido();
    setTexto(textoCorregido);
    // Recorregir para ver si quedan errores
    setTimeout(() => {
      corregirTexto();
    }, 500);
  };

  const guardarComoEvidencia = async () => {
    if (!estudianteSeleccionado) {
      toast.error('Selecciona un estudiante para guardar la corrección');
      return;
    }

    if (!correccion) {
      toast.error('Primero debes corregir el texto');
      return;
    }

    setGuardandoEvidencia(true);

    try {
      const textoCorregido = generarTextoCorregido();
      
      const formData = new FormData();
      formData.append('student_id', estudianteSeleccionado.id);
      formData.append('title', tituloCorreccion || `Corrección de ${estudianteSeleccionado.name}`);
      formData.append('original_text', texto);
      formData.append('corrected_text', textoCorregido); // Usar el texto corregido automáticamente
      formData.append('correction_type', 'texto');
      formData.append('language_tool_matches', JSON.stringify(correccion.matches || []));
      formData.append('statistics', JSON.stringify(estadisticas || {}));
      formData.append('teacher_feedback', comentarioProfesor);

      if (asignaturaSeleccionada) {
        formData.append('subject_id', asignaturaSeleccionada.id);
      }

      const response = await api.post('/correccion/guardar-evidencia/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      toast.success('Corrección guardada como evidencia exitosamente');
      
      // Limpiar formulario
      setEstudianteSeleccionado(null);
      setAsignaturaSeleccionada(null);
      setTituloCorreccion('');
      setComentarioProfesor('');
      
      if (onCorreccionCompleta) {
        onCorreccionCompleta(response.data);
      }

    } catch (err) {
      console.error('Error guardando evidencia:', err);
      toast.error('Error al guardar la evidencia');
    } finally {
      setGuardandoEvidencia(false);
    }
  };

  const limpiarCorreccion = () => {
    setCorreccion(null);
    setError(null);
    setMostrarSugerencias({});
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center">
          <BookOpen className="mr-2 h-5 w-5 text-blue-600" />
          Corrección de Texto
        </h3>
        {estadisticas && (
          <div className="flex items-center text-sm text-gray-600">
            <BarChart3 className="mr-1 h-4 w-4" />
            {estadisticas.total_palabras} palabras
          </div>
        )}
      </div>

      {/* Selector de idioma (OBLIGATORIO) */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Idioma del texto: <span className="text-red-600">*</span>
        </label>
        <select
          value={idioma}
          onChange={(e) => setIdioma(e.target.value)}
          className={`w-full px-3 py-2 bg-white text-gray-900 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
            !idioma ? 'border-red-300' : 'border-gray-300'
          }`}
        >
          <option value="">-- Selecciona el idioma --</option>
          <option value="ca">🏴 Català</option>
          <option value="es">�� Castellano</option>
          <option value="en">�� English</option>
        </select>
        {!idioma && (
          <p className="mt-1 text-xs text-red-600">
            ⚠️ Debes seleccionar el idioma antes de corregir
          </p>
        )}
      </div>

      {/* Área de texto */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Escribe tu texto aquí:
        </label>
        <textarea
          ref={textareaRef}
          value={texto}
          onChange={(e) => setTexto(e.target.value)}
          placeholder="Escribe aquí el texto que quieres corregir..."
          className="w-full h-32 px-3 py-2 bg-white text-gray-900 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none placeholder:text-gray-400"
        />
      </div>

      {/* Selección de estudiante y asignatura */}
      <div className="mb-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <h4 className="text-sm font-medium text-blue-900 mb-3 flex items-center">
          <User className="mr-2 h-4 w-4" />
          Vincular corrección con alumno
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Estudiante:
            </label>
            <select
              value={estudianteSeleccionado?.id || ''}
              onChange={(e) => {
                const estudiante = estudiantes.find(s => s.id === parseInt(e.target.value));
                setEstudianteSeleccionado(estudiante);
              }}
              className="w-full p-2 bg-white text-gray-900 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Selecciona un estudiante</option>
              {Array.isArray(estudiantes) && estudiantes.map(estudiante => (
                <option key={estudiante.id} value={estudiante.id}>
                  {estudiante.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Asignatura (opcional):
            </label>
            <select
              value={asignaturaSeleccionada?.id || ''}
              onChange={(e) => {
                const asignatura = asignaturas.find(s => s.id === parseInt(e.target.value));
                setAsignaturaSeleccionada(asignatura);
              }}
              className="w-full p-2 bg-white text-gray-900 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Selecciona una asignatura</option>
              {Array.isArray(asignaturas) && asignaturas.map(asignatura => (
                <option key={asignatura.id} value={asignatura.id}>
                  {asignatura.name}
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="mt-3">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Título de la corrección:
          </label>
          <input
            type="text"
            value={tituloCorreccion}
            onChange={(e) => setTituloCorreccion(e.target.value)}
            placeholder="Ej: Redacción sobre el medio ambiente"
            className="w-full p-2 bg-white text-gray-900 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 placeholder:text-gray-400"
          />
        </div>
        <div className="mt-3">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Comentario del profesor (opcional):
          </label>
          <textarea
            value={comentarioProfesor}
            onChange={(e) => setComentarioProfesor(e.target.value)}
            placeholder="Comentarios adicionales sobre la corrección..."
            className="w-full h-20 p-2 bg-white text-gray-900 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none placeholder:text-gray-400"
          />
        </div>
      </div>

      {/* Estadísticas en tiempo real */}
      {estadisticas && (
        <div className="mb-4 p-3 bg-gray-50 rounded-lg">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <span className="text-gray-600">Palabras:</span>
              <span className="ml-1 font-medium">{estadisticas.total_palabras}</span>
            </div>
            <div>
              <span className="text-gray-600">Caracteres:</span>
              <span className="ml-1 font-medium">{estadisticas.total_caracteres}</span>
            </div>
            <div>
              <span className="text-gray-600">Oraciones:</span>
              <span className="ml-1 font-medium">{estadisticas.total_oraciones}</span>
            </div>
            <div>
              <span className="text-gray-600">Promedio:</span>
              <span className="ml-1 font-medium">{estadisticas.promedio_palabras_por_oracion}</span>
            </div>
          </div>
        </div>
      )}

      {/* Botones de acción */}
      <div className="flex gap-2 mb-4">
        <button
          onClick={corregirTexto}
          disabled={loading || !texto.trim()}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : (
            <CheckCircle className="mr-2 h-4 w-4" />
          )}
          {loading ? 'Corrigiendo...' : 'Corregir Texto'}
        </button>

        {correccion && (
          <button
            onClick={limpiarCorreccion}
            className="px-4 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600"
          >
            Limpiar
          </button>
        )}

        {correccion && estudianteSeleccionado && (
          <button
            onClick={guardarComoEvidencia}
            disabled={guardandoEvidencia}
            className="flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {guardandoEvidencia ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Save className="mr-2 h-4 w-4" />
            )}
            {guardandoEvidencia ? 'Guardando...' : 'Guardar como Evidencia'}
          </button>
        )}
      </div>

      {/* Error */}
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
          <div className="flex items-center">
            <AlertCircle className="mr-2 h-4 w-4 text-red-600" />
            <span className="text-red-800 text-sm">{error}</span>
          </div>
        </div>
      )}

      {/* Resultados de corrección */}
      {correccion && (
        <div className="space-y-4">
          {/* Resumen de errores */}
          <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <h4 className="font-medium text-blue-900 mb-2">Resumen de Corrección</h4>
            <div className="text-sm text-blue-800">
              <p>Se encontraron <span className="font-semibold">{correccion.total_errors}</span> errores en el texto.</p>
              <p>Idioma detectado: <span className="font-semibold">{correccion.detected_language}</span></p>
            </div>
          </div>

          {/* Texto con errores marcados */}
          <div className="p-4 border border-gray-200 rounded-lg bg-gray-50">
            <div className="flex items-center justify-between mb-3">
              <h4 className="font-medium text-gray-900">Texto con Errores Marcados</h4>
              <button
                onClick={aplicarTodasLasCorrecciones}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center text-sm"
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Aplicar todas las correcciones
              </button>
            </div>
            <div className="text-sm leading-relaxed text-gray-900 mb-3">
              {renderizarTextoConErrores()}
            </div>
            <div className="mt-2 text-xs text-gray-600">
              💡 Haz clic en las palabras marcadas para ver sugerencias de corrección
            </div>
          </div>

          {/* Texto completamente corregido */}
          <div className="p-4 border border-green-200 rounded-lg bg-green-50">
            <h4 className="font-medium text-green-900 mb-2 flex items-center">
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Texto Corregido (Automático)
            </h4>
            <div className="text-sm leading-relaxed text-green-900 p-3 bg-white rounded border border-green-200">
              {generarTextoCorregido()}
            </div>
            <div className="mt-2 text-xs text-green-700">
              ✨ Este es el texto con todas las correcciones aplicadas automáticamente
            </div>
          </div>

          {/* Lista detallada de errores */}
          {correccion.matches && correccion.matches.length > 0 && (
            <div className="p-4 border border-gray-200 rounded-lg">
              <h4 className="font-medium text-gray-900 mb-3">Errores Encontrados</h4>
              <div className="space-y-2">
                {correccion.matches.map((error, index) => (
                  <div key={index} className="p-3 bg-white border border-gray-200 rounded-md">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="font-medium text-gray-900">
                          "{texto.substring(error.offset, error.offset + error.length)}"
                        </div>
                        <div className="text-sm text-gray-600 mt-1">
                          {error.message}
                        </div>
                        {error.suggestions && error.suggestions.length > 0 && (
                          <div className="mt-2">
                            <div className="text-xs text-gray-500 mb-1">Sugerencias:</div>
                            <div className="flex flex-wrap gap-1">
                              {error.suggestions.map((sugerencia, idx) => (
                                <span
                                  key={idx}
                                  className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded"
                                >
                                  {sugerencia.value}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                      <div className="ml-2">
                        <span className={`px-2 py-1 text-xs rounded ${
                          error.severity === 'alta' ? 'bg-red-100 text-red-800' :
                          error.severity === 'media' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-blue-100 text-blue-800'
                        }`}>
                          {error.severity}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default CorreccionTexto;
