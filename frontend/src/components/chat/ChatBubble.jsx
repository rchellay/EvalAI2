import PaperCard from './PaperCard';

export default function ChatBubble({ message }) {
  const isUser = message.sender === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-3xl ${isUser ? 'order-2' : 'order-1'}`}>
        {/* Sender Label */}
        <div className={`text-xs font-semibold mb-1 ${isUser ? 'text-right' : 'text-left'} text-gray-600`}>
          {isUser ? 'Tú' : '🤖 Asistente de Investigación'}
        </div>

        {/* Message Bubble */}
        <div
          className={`rounded-lg px-4 py-3 ${
            isUser
              ? 'bg-blue-600 text-white rounded-br-none'
              : 'bg-white text-gray-800 border border-gray-200 rounded-bl-none shadow-sm'
          }`}
        >
          <div className="whitespace-pre-wrap leading-relaxed">{message.content}</div>

          {/* Timestamp */}
          <div
            className={`text-xs mt-2 ${
              isUser ? 'text-blue-100' : 'text-gray-500'
            }`}
          >
            {new Date(message.timestamp).toLocaleTimeString('es-ES', {
              hour: '2-digit',
              minute: '2-digit'
            })}
          </div>
        </div>

        {/* Papers Section (only for assistant) */}
        {!isUser && message.papers && Array.isArray(message.papers) && message.papers.length > 0 && (
          <div className="mt-3 space-y-2">
            <div className="text-xs font-semibold text-gray-600 mb-2">
              📚 Estudios citados ({message.papers.length}):
            </div>
            {message.papers.map((paper, index) => (
              <PaperCard key={index} paper={paper} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
