import React, { useState } from 'react';
import { BookOpen, Users, FileText, CheckCircle, Camera } from 'lucide-react';
import CorreccionTexto from '../components/CorreccionTexto';
import OCRImagen from '../components/OCRImagen';

const CorreccionPage = () => {
  const [correccionesRealizadas, setCorreccionesRealizadas] = useState(0);
  const [herramientaActiva, setHerramientaActiva] = useState('texto'); // 'texto' o 'ocr'

  const handleCorreccionCompleta = (data) => {
    setCorreccionesRealizadas(prev => prev + 1);
    console.log('Corrección completada:', data);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-200">
      {/* Header */}
      <div className="bg-white/70 backdrop-blur-sm shadow-md border-b border-white/20">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <h1 className="text-4xl font-bold text-slate-800 flex items-center">
            <BookOpen className="mr-3 h-10 w-10 text-blue-600" />
            Corrección de Texto
          </h1>
          <p className="text-slate-600 mt-2">
            Herramienta de corrección gramatical y ortográfica con LanguageTool API
          </p>
        </div>
      </div>

      {/* Contenido principal */}
      <div className="max-w-7xl mx-auto p-6">
        {/* Selector de herramientas */}
        <div className="mb-6">
          <div className="flex bg-white rounded-lg p-1 shadow-sm border border-gray-200">
            <button
              onClick={() => setHerramientaActiva('texto')}
              className={`flex-1 flex items-center justify-center px-4 py-2 rounded-md transition-colors ${
                herramientaActiva === 'texto'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50'
              }`}
            >
              <FileText size={20} className="mr-2" />
              Corrección de Texto
            </button>
            <button
              onClick={() => setHerramientaActiva('ocr')}
              className={`flex-1 flex items-center justify-center px-4 py-2 rounded-md transition-colors ${
                herramientaActiva === 'ocr'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50'
              }`}
            >
              <Camera size={20} className="mr-2" />
              OCR Manuscrito
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Panel principal */}
          <div className="lg:col-span-2">
            {herramientaActiva === 'texto' ? (
              <CorreccionTexto 
                onCorreccionCompleta={handleCorreccionCompleta}
              />
            ) : (
              <OCRImagen />
            )}
          </div>

          {/* Panel lateral con información */}
          <div className="space-y-6">
            {/* Estadísticas */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <CheckCircle className="mr-2 h-5 w-5 text-green-600" />
                Estadísticas
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Correcciones realizadas:</span>
                  <span className="font-semibold text-blue-600">{correccionesRealizadas}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Estado del servicio:</span>
                  <span className="font-semibold text-green-600">Activo</span>
                </div>
              </div>
            </div>

            {/* Información educativa */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Users className="mr-2 h-5 w-5 text-purple-600" />
                Valor Educativo
              </h3>
              <div className="space-y-3 text-sm text-gray-700">
                {herramientaActiva === 'texto' ? (
                  <>
                    <div className="flex items-start">
                      <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                      <span>Mejora la escritura y comprensión ortográfica</span>
                    </div>
                    <div className="flex items-start">
                      <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                      <span>Ideal para primaria: corrige errores básicos</span>
                    </div>
                    <div className="flex items-start">
                      <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                      <span>Enseña ortografía de forma interactiva</span>
                    </div>
                    <div className="flex items-start">
                      <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                      <span>Proporciona sugerencias contextuales</span>
                    </div>
                  </>
                ) : (
                  <>
                    <div className="flex items-start">
                      <div className="w-2 h-2 bg-green-500 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                      <span>Escanea escritura manuscrita de alumnos</span>
                    </div>
                    <div className="flex items-start">
                      <div className="w-2 h-2 bg-green-500 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                      <span>Perfecto para fichas escritas a mano</span>
                    </div>
                    <div className="flex items-start">
                      <div className="w-2 h-2 bg-green-500 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                      <span>Corrección automática de textos escaneados</span>
                    </div>
                    <div className="flex items-start">
                      <div className="w-2 h-2 bg-green-500 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                      <span>Soporte para español manuscrito</span>
                    </div>
                  </>
                )}
              </div>
            </div>

            {/* Características técnicas */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <FileText className="mr-2 h-5 w-5 text-orange-600" />
                Características
              </h3>
              <div className="space-y-2 text-sm text-gray-700">
                {herramientaActiva === 'texto' ? (
                  <>
                    <div>✅ Corrección ortográfica</div>
                    <div>✅ Corrección gramatical</div>
                    <div>✅ Sugerencias contextuales</div>
                    <div>✅ Estadísticas de texto</div>
                    <div>✅ Interfaz educativa</div>
                    <div>✅ Soporte para español</div>
                  </>
                ) : (
                  <>
                    <div>✅ OCR manuscrito (Google Cloud Vision)</div>
                    <div>✅ Soporte español manuscrito</div>
                    <div>✅ Múltiples formatos de imagen</div>
                    <div>✅ Validación automática</div>
                    <div>✅ Corrección integrada</div>
                    <div>✅ Interfaz intuitiva</div>
                  </>
                )}
              </div>
            </div>

            {/* Instrucciones de uso */}
            <div className="bg-blue-50 rounded-lg border border-blue-200 p-6">
              <h3 className="text-lg font-semibold text-blue-900 mb-3">
                📝 Cómo usar
              </h3>
              <div className="space-y-2 text-sm text-blue-800">
                {herramientaActiva === 'texto' ? (
                  <>
                    <div>1. Escribe tu texto en el área de texto</div>
                    <div>2. Haz clic en "Corregir Texto"</div>
                    <div>3. Revisa los errores marcados</div>
                    <div>4. Haz clic en las palabras marcadas para ver sugerencias</div>
                    <div>5. Aplica las correcciones que consideres apropiadas</div>
                  </>
                ) : (
                  <>
                    <div>1. Selecciona una imagen con texto manuscrito</div>
                    <div>2. Configura el idioma y tipo de texto</div>
                    <div>3. Haz clic en "Extraer y Corregir"</div>
                    <div>4. Revisa el texto extraído y las correcciones</div>
                    <div>5. Haz clic en palabras marcadas para ver sugerencias</div>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CorreccionPage;
