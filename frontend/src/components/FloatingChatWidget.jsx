import { useState, useEffect, useRef } from 'react';
import { X, Send, MessageCircle, Minimize2 } from 'lucide-react';
import api from '../lib/axios';

// Logo - reemplazar con: import comeniusLogo from '../assets/comenius-ai-logo.png';
const comeniusLogo = '/comenius-ai-logo-temp.svg';

export default function FloatingChatWidget() {
  const [user, setUser] = useState(null);
  const [isOpen, setIsOpen] = useState(() => {
    // Recuperar estado de localStorage
    const saved = localStorage.getItem('floatingChat_isOpen');
    return saved ? JSON.parse(saved) : false;
  });
  const [isMinimized, setIsMinimized] = useState(false);
  const [currentChat, setCurrentChat] = useState(() => {
    // Recuperar chat actual de localStorage
    const saved = localStorage.getItem('floatingChat_currentChat');
    return saved ? JSON.parse(saved) : null;
  });
  const [messages, setMessages] = useState(() => {
    // Recuperar mensajes de localStorage
    const saved = localStorage.getItem('floatingChat_messages');
    return saved ? JSON.parse(saved) : [];
  });
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Guardar estado en localStorage cuando cambie
  useEffect(() => {
    localStorage.setItem('floatingChat_isOpen', JSON.stringify(isOpen));
  }, [isOpen]);

  useEffect(() => {
    if (currentChat) {
      localStorage.setItem('floatingChat_currentChat', JSON.stringify(currentChat));
    }
  }, [currentChat]);

  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem('floatingChat_messages', JSON.stringify(messages));
    }
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load user data
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      api.get('/auth/me')
        .then(r => setUser(r.data))
        .catch(() => setUser(null));
    }
  }, []);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const messageText = inputMessage;
    setInputMessage('');
    setIsLoading(true);

    try {
      if (!currentChat) {
        // Start new chat
        const response = await api.post('/ai/chat/start_new/', {
          message: messageText
        });

        // Backend returns { chat: {...}, success: true }
        setCurrentChat(response.data.chat);
        setMessages(response.data.chat.messages || []);
      } else {
        // Send to existing chat
        const response = await api.post(`/ai/chat/${currentChat.id}/send_message/`, {
          message: messageText
        });

        setMessages(prev => [
          ...prev,
          response.data.user_message,
          response.data.assistant_message
        ]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      alert('Error al enviar mensaje');
    } finally {
      setIsLoading(false);
    }
  };

  const handleClose = () => {
    setIsOpen(false);
    setIsMinimized(false);
  };

  const handleNewChat = () => {
    setCurrentChat(null);
    setMessages([]);
    // Limpiar localStorage
    localStorage.removeItem('floatingChat_currentChat');
    localStorage.removeItem('floatingChat_messages');
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 z-50 w-16 h-16 bg-white rounded-full shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center group border-2 border-blue-600"
      >
        <img src={comeniusLogo} alt="ComeniusAI" className="w-12 h-12 object-contain group-hover:scale-110 transition-transform" />
        <span className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full animate-pulse"></span>
      </button>
    );
  }

  if (isMinimized) {
    return (
      <div className="fixed bottom-6 right-6 z-50 bg-white rounded-lg shadow-lg p-4 cursor-pointer hover:shadow-xl transition-shadow" onClick={() => setIsMinimized(false)}>
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center p-1">
            <img src={comeniusLogo} alt="ComeniusAI" className="w-full h-full object-contain" />
          </div>
          <div>
            <div className="font-semibold text-gray-800">ComeniusAI</div>
            <div className="text-xs text-gray-500">{messages.length} mensajes</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed bottom-6 right-6 z-50 w-96 h-[600px] bg-white rounded-2xl shadow-2xl flex flex-col overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center p-1">
            <img src={comeniusLogo} alt="ComeniusAI" className="w-full h-full object-contain" />
          </div>
          <div>
            <div className="font-semibold">ComeniusAI</div>
            <div className="text-xs text-blue-100">Asistente educativo basado en evidencia</div>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setIsMinimized(true)}
            className="p-1 hover:bg-white/20 rounded transition-colors"
          >
            <Minimize2 size={18} />
          </button>
          <button
            onClick={handleClose}
            className="p-1 hover:bg-white/20 rounded transition-colors"
          >
            <X size={18} />
          </button>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center px-4">
            <img src={comeniusLogo} alt="ComeniusAI" className="w-20 h-20 mb-4" />
            <h3 className="text-lg font-bold text-gray-800 mb-3">
              ¡Hola! Soy ComeniusAI, tu asistente educativo basado en evidencia.
            </h3>
            <p className="text-sm text-gray-700 mb-3 leading-relaxed">
              ¿Tienes dudas sobre <strong>metodologías, evaluación, motivación</strong> o <strong>gestión de aula</strong>?
            </p>
            <p className="text-sm text-gray-600 mb-4">
              Te daré respuestas rápidas apoyadas en investigaciones científicas reales.
            </p>
            <div className="text-xs text-gray-500 bg-white p-3 rounded-lg border border-gray-200 space-y-1">
              <p className="font-semibold text-gray-700">💡 Ejemplos:</p>
              <p>"¿Qué dice la evidencia sobre aprendizaje cooperativo?"</p>
              <p>"¿Cómo mejorar la motivación según la investigación?"</p>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg px-3 py-2 ${
                    msg.sender === 'user'
                      ? 'bg-blue-600 text-white rounded-br-none'
                      : 'bg-white text-gray-800 border border-gray-200 rounded-bl-none'
                  }`}
                >
                  <div className="text-sm whitespace-pre-wrap">{msg.content}</div>
                  {msg.papers && msg.papers.length > 0 && (
                    <div className="mt-2 text-xs space-y-1">
                      <div className="font-semibold">📚 Papers citados:</div>
                      {msg.papers.slice(0, 2).map((paper, pidx) => (
                        <div key={pidx} className="bg-blue-50 p-2 rounded">
                          <div className="font-medium">{paper.title}</div>
                          <div className="text-gray-600">
                            {paper.authors?.slice(0, 2).join(', ')} ({paper.year})
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-600">
                  <div className="flex items-center space-x-2">
                    <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-blue-600"></div>
                    <span>Buscando papers...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="border-t bg-white p-3">
        {messages.length > 0 && (
          <button
            onClick={handleNewChat}
            className="w-full mb-2 px-3 py-1.5 text-xs text-blue-600 hover:bg-blue-50 rounded transition-colors"
          >
            + Nueva conversación
          </button>
        )}
        <div className="flex items-center space-x-2">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSendMessage()}
            placeholder="Pregunta sobre educación..."
            disabled={isLoading}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm disabled:bg-gray-100"
          />
          <button
            onClick={handleSendMessage}
            disabled={isLoading || !inputMessage.trim()}
            className="p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}
