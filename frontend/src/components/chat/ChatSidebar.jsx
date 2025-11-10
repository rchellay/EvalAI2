export default function ChatSidebar({ chatSessions, currentChatId, onSelectChat, onNewChat, isOpen, onToggle }) {
  return (
    <>
      {/* Toggle Button (mobile) */}
      <button
        onClick={onToggle}
        className="fixed top-4 left-4 z-50 md:hidden bg-white p-2 rounded-lg shadow-lg"
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>

      {/* Sidebar */}
      <div
        className={`${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        } md:translate-x-0 fixed md:relative z-40 w-80 bg-white border-r h-full transition-transform duration-300 ease-in-out flex flex-col`}
      >
        {/* Header */}
        <div className="p-4 border-b">
          <button
            onClick={onNewChat}
            className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium flex items-center justify-center space-x-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            <span>Nueva Conversación</span>
          </button>
        </div>

        {/* Chat List */}
        <div className="flex-1 overflow-y-auto p-4">
          <h3 className="text-sm font-semibold text-gray-600 mb-3 uppercase tracking-wide">
            Conversaciones
          </h3>
          
          {chatSessions.length === 0 ? (
            <div className="text-center text-gray-500 text-sm mt-8">
              <p>No hay conversaciones aún</p>
              <p className="text-xs mt-2">Inicia una nueva para comenzar</p>
            </div>
          ) : (
            <div className="space-y-2">
              {chatSessions.map((session) => (
                <button
                  key={session.id}
                  onClick={() => onSelectChat(session.id)}
                  className={`w-full text-left p-3 rounded-lg transition-colors ${
                    currentChatId === session.id
                      ? 'bg-blue-50 border-2 border-blue-600'
                      : 'bg-gray-50 hover:bg-gray-100 border-2 border-transparent'
                  }`}
                >
                  <div className="font-medium text-gray-800 truncate mb-1">
                    {session.title || 'Nueva conversación'}
                  </div>
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>{session.message_count} mensajes</span>
                    <span>
                      {new Date(session.updated_at).toLocaleDateString('es-ES', {
                        day: 'numeric',
                        month: 'short'
                      })}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Footer Info */}
        <div className="p-4 border-t bg-gray-50">
          <div className="text-xs text-gray-600 space-y-1">
            <p className="font-semibold">🔬 Fuentes científicas:</p>
            <p>• Semantic Scholar</p>
            <p>• OpenAlex</p>
          </div>
        </div>
      </div>

      {/* Overlay (mobile) */}
      {isOpen && (
        <div
          onClick={onToggle}
          className="fixed inset-0 bg-black bg-opacity-50 z-30 md:hidden"
        />
      )}
    </>
  );
}
