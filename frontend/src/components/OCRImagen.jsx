import React, { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { Camera, Upload, FileImage, CheckCircle, AlertCircle, Loader2, Eye, Edit3, User, Save } from 'lucide-react';
import api from '../lib/axios';
import { toast } from 'react-hot-toast';

const OCRImagen = () => {
  const [imagen, setImagen] = useState(null);
  const [imagenPreview, setImagenPreview] = useState(null);
  const [textoExtraido, setTextoExtraido] = useState('');
  const [correccion, setCorreccion] = useState(null);
  const [estadisticas, setEstadisticas] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [idioma, setIdioma] = useState('es-t-i0-handwrit');
  const [tipoTexto, setTipoTexto] = useState('manuscrito');
  const [mostrarSugerencias, setMostrarSugerencias] = useState({});
  const [idiomasDisponibles, setIdiomasDisponibles] = useState({});
  const [validacionImagen, setValidacionImagen] = useState(null);
  
  // Estados para vincular con alumno
  const [estudiantes, setEstudiantes] = useState([]);
  const [estudianteSeleccionado, setEstudianteSeleccionado] = useState(null);
  const [asignaturaSeleccionada, setAsignaturaSeleccionada] = useState(null);
  const [asignaturas, setAsignaturas] = useState([]);
  const [tituloCorreccion, setTituloCorreccion] = useState('');
  const [comentarioProfesor, setComentarioProfesor] = useState('');
  const [guardandoEvidencia, setGuardandoEvidencia] = useState(false);
  
  const fileInputRef = useRef(null);

  // Cargar idiomas disponibles y datos al montar el componente
  React.useEffect(() => {
    cargarIdiomasDisponibles();
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

  const cargarIdiomasDisponibles = async () => {
    try {
      const response = await api.get('/ocr/idiomas/');
      setIdiomasDisponibles(response.data.idiomas);
    } catch (err) {
      console.error('Error cargando idiomas:', err);
    }
  };

  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      setImagen(file);
      
      // Crear preview
      const reader = new FileReader();
      reader.onload = (e) => {
        setImagenPreview(e.target.result);
      };
      reader.readAsDataURL(file);
      
      // Validar imagen
      validarImagen(file);
      
      // Limpiar estados anteriores
      setTextoExtraido('');
      setCorreccion(null);
      setEstadisticas(null);
      setError(null);
    }
  };

  const validarImagen = async (file) => {
    try {
      const formData = new FormData();
      formData.append('imagen', file);
      
      const response = await api.post('/ocr/validar/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      setValidacionImagen(response.data);
      
      if (!response.data.valida) {
        toast.error(response.data.error);
      }
    } catch (err) {
      console.error('Error validando imagen:', err);
    }
  };

  const procesarImagenOCR = async () => {
    if (!imagen) {
      toast.error('Selecciona una imagen primero');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('imagen', imagen);
      formData.append('idioma', idioma);
      formData.append('tipo', tipoTexto);

      const response = await api.post('/ocr/procesar/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      console.log('Respuesta OCR:', response.data);
      setTextoExtraido(response.data.text);
      console.log('Texto extraído establecido:', response.data.text);
      toast.success('Texto extraído exitosamente');
    } catch (err) {
      console.error('Error procesando imagen:', err);
      setError(err.response?.data?.error || 'Error al procesar la imagen');
      toast.error('Error al procesar la imagen');
    } finally {
      setLoading(false);
    }
  };

  const procesarYCorregirImagen = async () => {
    if (!imagen) {
      toast.error('Selecciona una imagen primero');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('imagen', imagen);
      formData.append('idioma', idioma);
      formData.append('tipo', tipoTexto);

      const response = await api.post('/ocr/procesar-y-corregir/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      console.log('Respuesta OCR con corrección:', response.data);
      setTextoExtraido(response.data.texto_original);
      setCorreccion(response.data.texto_corregido);
      console.log('Texto original:', response.data.texto_original);
      console.log('Texto corregido:', response.data.texto_corregido);
      setEstadisticas(response.data.estadisticas);
      toast.success('Imagen procesada y texto corregido exitosamente');
    } catch (err) {
      console.error('Error procesando imagen:', err);
      setError(err.response?.data?.error || 'Error al procesar la imagen');
      toast.error('Error al procesar la imagen');
    } finally {
      setLoading(false);
    }
  };

  const renderizarTextoConErrores = () => {
    if (!correccion || !correccion.matches) return textoExtraido;

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
          <span key={`texto-${index}`}>
            {textoExtraido.substring(ultimoIndice, inicio)}
          </span>
        );
      }

      // Agregar el error marcado
      const claseSeveridad = {
        'alta': 'bg-red-200 border-red-400 text-red-800',
        'media': 'bg-yellow-200 border-yellow-400 text-yellow-800',
        'baja': 'bg-blue-200 border-blue-400 text-blue-800'
      }[error.severity] || 'bg-gray-200 border-gray-400 text-gray-800';

      elementos.push(
        <span
          key={`error-${index}`}
          className={`relative inline-block px-1 py-0.5 rounded border-b-2 cursor-pointer ${claseSeveridad}`}
          onClick={() => setMostrarSugerencias({ [inicio]: !mostrarSugerencias[inicio] })}
          title={`${error.message} - Click para ver sugerencias`}
        >
          {textoExtraido.substring(inicio, fin)}
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
    if (ultimoIndice < textoExtraido.length) {
      elementos.push(
        <span key="texto-final">
          {textoExtraido.substring(ultimoIndice)}
        </span>
      );
    }

    return elementos;
  };

  const aplicarSugerencia = (inicio, fin, sugerencia) => {
    const nuevoTexto = textoExtraido.substring(0, inicio) + sugerencia + textoExtraido.substring(fin);
    setTextoExtraido(nuevoTexto);
    setMostrarSugerencias({});
  };

  const guardarComoEvidencia = async () => {
    if (!estudianteSeleccionado) {
      toast.error('Selecciona un estudiante para guardar la corrección');
      return;
    }

    if (!textoExtraido || !correccion) {
      toast.error('Primero debes procesar y corregir la imagen');
      return;
    }

    setGuardandoEvidencia(true);

    try {
      const formData = new FormData();
      formData.append('student_id', estudianteSeleccionado.id);
      formData.append('title', tituloCorreccion || `Corrección OCR de ${estudianteSeleccionado.name}`);
      formData.append('original_text', textoExtraido);
      formData.append('corrected_text', textoExtraido); // El texto ya está corregido
      formData.append('correction_type', 'ocr');
      formData.append('language_tool_matches', JSON.stringify(correccion.matches || []));
      formData.append('ocr_info', JSON.stringify({
        idioma: idioma,
        tipo: tipoTexto,
        confianza: 0.9 // Valor por defecto
      }));
      formData.append('statistics', JSON.stringify(estadisticas || {}));
      formData.append('teacher_feedback', comentarioProfesor);

      if (asignaturaSeleccionada) {
        formData.append('subject_id', asignaturaSeleccionada.id);
      }

      if (imagen) {
        formData.append('imagen', imagen); // Usar siempre 'imagen' para consistencia con backend
      }

      const response = await api.post('/correccion/guardar-evidencia/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      toast.success('Corrección OCR guardada como evidencia exitosamente');
      
      // Limpiar formulario
      setEstudianteSeleccionado(null);
      setAsignaturaSeleccionada(null);
      setTituloCorreccion('');
      setComentarioProfesor('');

    } catch (err) {
      console.error('Error guardando evidencia:', err);
      toast.error('Error al guardar la evidencia');
    } finally {
      setGuardandoEvidencia(false);
    }
  };

  const limpiarTodo = () => {
    setImagen(null);
    setImagenPreview(null);
    setTextoExtraido('');
    setCorreccion(null);
    setEstadisticas(null);
    setError(null);
    setValidacionImagen(null);
    setMostrarSugerencias({});
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="bg-white dark:bg-slate-900 p-6 rounded-lg shadow-md border border-slate-200 dark:border-slate-800"
    >
      <h2 className="text-2xl font-bold text-slate-800 dark:text-white mb-4 flex items-center">
        <Camera className="mr-2 text-blue-500" /> OCR para Escritura Manuscrita
      </h2>
      <p className="text-slate-600 dark:text-slate-400 mb-6">
        Escanea y transcribe escritura a mano de tus alumnos para corrección automática.
      </p>

      {/* Configuración */}
      <div className="mb-6 p-4 bg-slate-50 dark:bg-slate-800 rounded-lg">
        <h3 className="text-lg font-semibold text-slate-800 dark:text-white mb-3">Configuración</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              Idioma:
            </label>
            <select
              value={idioma}
              onChange={(e) => setIdioma(e.target.value)}
              className="w-full p-2 border border-slate-300 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white"
            >
              {Object.entries(idiomasDisponibles).map(([codigo, nombre]) => (
                <option key={codigo} value={codigo}>{nombre}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              Tipo de texto:
            </label>
            <select
              value={tipoTexto}
              onChange={(e) => setTipoTexto(e.target.value)}
              className="w-full p-2 border border-slate-300 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white"
            >
              <option value="manuscrito">Manuscrito</option>
              <option value="impreso">Impreso</option>
            </select>
          </div>
        </div>
      </div>

      {/* Selección de estudiante y asignatura */}
      <div className="mb-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
        <h4 className="text-sm font-medium text-blue-900 dark:text-blue-100 mb-3 flex items-center">
          <User className="mr-2 h-4 w-4" />
          Vincular corrección con alumno
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Estudiante:
            </label>
            <select
              value={estudianteSeleccionado?.id || ''}
              onChange={(e) => {
                const estudiante = estudiantes.find(s => s.id === parseInt(e.target.value));
                setEstudianteSeleccionado(estudiante);
              }}
              className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
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
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Asignatura (opcional):
            </label>
            <select
              value={asignaturaSeleccionada?.id || ''}
              onChange={(e) => {
                const asignatura = asignaturas.find(s => s.id === parseInt(e.target.value));
                setAsignaturaSeleccionada(asignatura);
              }}
              className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
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
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Título de la corrección:
          </label>
          <input
            type="text"
            value={tituloCorreccion}
            onChange={(e) => setTituloCorreccion(e.target.value)}
            placeholder="Ej: Redacción manuscrita sobre el medio ambiente"
            className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
          />
        </div>
        <div className="mt-3">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Comentario del profesor (opcional):
          </label>
          <textarea
            value={comentarioProfesor}
            onChange={(e) => setComentarioProfesor(e.target.value)}
            placeholder="Comentarios adicionales sobre la corrección..."
            className="w-full h-20 p-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
          />
        </div>
      </div>

      {/* Carga de imagen */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
          Selecciona una imagen:
        </label>
        <div className="border-2 border-dashed border-slate-300 dark:border-slate-700 rounded-lg p-6 text-center">
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleImageUpload}
            className="hidden"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            className="flex flex-col items-center justify-center w-full h-32 text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200"
          >
            <Upload size={48} className="mb-2" />
            <span className="text-sm">Haz clic para seleccionar una imagen</span>
            <span className="text-xs text-slate-400">JPG, PNG, GIF, BMP, WEBP (máx. 20MB)</span>
          </button>
        </div>

        {/* Preview de imagen */}
        {imagenPreview && (
          <div className="mt-4">
            <h4 className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Vista previa:</h4>
            <img
              src={imagenPreview}
              alt="Preview"
              className="max-w-full h-64 object-contain border border-slate-300 dark:border-slate-700 rounded-lg"
            />
          </div>
        )}

        {/* Validación de imagen */}
        {validacionImagen && (
          <div className={`mt-4 p-3 rounded-lg ${
            validacionImagen.valida 
              ? 'bg-green-50 dark:bg-green-900 text-green-800 dark:text-green-200' 
              : 'bg-red-50 dark:bg-red-900 text-red-800 dark:text-red-200'
          }`}>
            <div className="flex items-center">
              {validacionImagen.valida ? (
                <CheckCircle size={20} className="mr-2" />
              ) : (
                <AlertCircle size={20} className="mr-2" />
              )}
              <span className="font-medium">
                {validacionImagen.valida ? 'Imagen válida' : validacionImagen.error}
              </span>
            </div>
            {validacionImagen.sugerencias && validacionImagen.sugerencias.length > 0 && (
              <div className="mt-2">
                <p className="text-sm font-medium mb-1">Sugerencias:</p>
                <ul className="text-sm list-disc list-inside">
                  {validacionImagen.sugerencias.map((sugerencia, index) => (
                    <li key={index}>{sugerencia}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Botones de acción */}
      <div className="flex gap-3 mb-6">
        <button
          onClick={procesarImagenOCR}
          disabled={loading || !imagen}
          className="flex items-center px-4 py-2 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-slate-900 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? (
            <Loader2 size={20} className="mr-2 animate-spin" />
          ) : (
            <Eye size={20} className="mr-2" />
          )}
          {loading ? 'Procesando...' : 'Extraer Texto'}
        </button>

        <button
          onClick={procesarYCorregirImagen}
          disabled={loading || !imagen}
          className="flex items-center px-4 py-2 bg-green-600 text-white font-semibold rounded-lg shadow-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 dark:focus:ring-offset-slate-900 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? (
            <Loader2 size={20} className="mr-2 animate-spin" />
          ) : (
            <Edit3 size={20} className="mr-2" />
          )}
          {loading ? 'Procesando...' : 'Extraer y Corregir'}
        </button>

        <button
          onClick={limpiarTodo}
          className="px-4 py-2 bg-gray-500 text-white font-semibold rounded-lg shadow-md hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 dark:focus:ring-offset-slate-900 transition-colors"
        >
          Limpiar Todo
        </button>

        {textoExtraido && correccion && estudianteSeleccionado && (
          <button
            onClick={guardarComoEvidencia}
            disabled={guardandoEvidencia}
            className="flex items-center px-4 py-2 bg-purple-600 text-white font-semibold rounded-lg shadow-md hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 dark:focus:ring-offset-slate-900 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {guardandoEvidencia ? (
              <Loader2 size={20} className="mr-2 animate-spin" />
            ) : (
              <Save size={20} className="mr-2" />
            )}
            {guardandoEvidencia ? 'Guardando...' : 'Guardar como Evidencia'}
          </button>
        )}
      </div>

      {/* Error */}
      {error && (
        <div className="mb-6 p-3 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 rounded-lg flex items-center">
          <AlertCircle size={20} className="mr-2" /> {error}
        </div>
      )}

      {/* Texto extraído */}
      {textoExtraido && (
        <div className="mb-6 p-4 bg-blue-50 dark:bg-slate-800 rounded-lg border border-blue-200 dark:border-slate-700">
          <h3 className="text-lg font-semibold text-slate-800 dark:text-white mb-3 flex items-center">
            <FileImage className="mr-2 text-blue-600" /> Texto Extraído
          </h3>
          <div className="text-slate-700 dark:text-slate-300 text-base leading-relaxed">
            {correccion ? renderizarTextoConErrores() : textoExtraido}
          </div>
          {correccion && (
            <div className="mt-2 text-xs text-slate-600 dark:text-slate-400">
              💡 Haz clic en las palabras marcadas para ver sugerencias de corrección
            </div>
          )}
        </div>
      )}

      {/* Estadísticas */}
      {estadisticas && (
        <div className="p-4 bg-green-50 dark:bg-slate-800 rounded-lg border border-green-200 dark:border-slate-700">
          <h3 className="text-lg font-semibold text-slate-800 dark:text-white mb-3 flex items-center">
            <CheckCircle className="mr-2 text-green-600" /> Estadísticas del Texto
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <span className="text-slate-600 dark:text-slate-400">Palabras:</span>
              <span className="ml-1 font-medium text-slate-800 dark:text-white">{estadisticas.total_palabras}</span>
            </div>
            <div>
              <span className="text-slate-600 dark:text-slate-400">Caracteres:</span>
              <span className="ml-1 font-medium text-slate-800 dark:text-white">{estadisticas.total_caracteres}</span>
            </div>
            <div>
              <span className="text-slate-600 dark:text-slate-400">Oraciones:</span>
              <span className="ml-1 font-medium text-slate-800 dark:text-white">{estadisticas.total_oraciones}</span>
            </div>
            <div>
              <span className="text-slate-600 dark:text-slate-400">Promedio:</span>
              <span className="ml-1 font-medium text-slate-800 dark:text-white">{estadisticas.promedio_palabras_por_oracion}</span>
            </div>
          </div>
        </div>
      )}
    </motion.div>
  );
};

export default OCRImagen;
