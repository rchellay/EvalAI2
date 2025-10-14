import { AlertCircle } from 'lucide-react';

export default function EditSeriesModal({ 
  isOpen, 
  onClose, 
  onEditThis, 
  onEditSeries,
  action = 'edit' // 'edit' or 'delete'
}) {
  if (!isOpen) return null;

  const actionText = action === 'delete' ? 'eliminar' : 'editar';
  const actionTextCap = action === 'delete' ? 'Eliminar' : 'Editar';

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-6">
        {/* Icon */}
        <div className="flex justify-center mb-4">
          <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
            <AlertCircle className="text-blue-600" size={24} />
          </div>
        </div>

        {/* Title */}
        <h2 className="text-xl font-bold text-gray-800 text-center mb-2">
          {actionTextCap} evento recurrente
        </h2>

        {/* Description */}
        <p className="text-gray-600 text-center mb-6">
          Este es un evento recurrente. ¿Deseas {actionText} solo esta ocurrencia o toda la serie?
        </p>

        {/* Actions */}
        <div className="space-y-3">
          <button
            onClick={onEditThis}
            className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition-colors"
          >
            Solo esta ocurrencia
          </button>

          <button
            onClick={onEditSeries}
            className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition-colors"
          >
            Toda la serie
          </button>

          <button
            onClick={onClose}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 font-medium transition-colors"
          >
            Cancelar
          </button>
        </div>
      </div>
    </div>
  );
}
