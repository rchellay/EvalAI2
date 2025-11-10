import { useState, useEffect, useRef } from 'react';
import api from '../lib/axios';
import ChatBubble from '../components/chat/ChatBubble';
import MessageInput from '../components/chat/MessageInput';
import ChatSidebar from '../components/chat/ChatSidebar';

// Logo - reemplazar con: import comeniusLogo from '../assets/comenius-ai-logo.png';
const comeniusLogo = '/comenius-ai-logo-temp.svg';

export default function AIExpertPage() {
  const [user, setUser] = useState(null);
  const [currentChat, setCurrentChat] = useState(null);
  const [messages, setMessages] = useState([]);
  const [chatSessions, setChatSessions] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const messagesEndRef = useRef(null);

  // Scroll to bottom when new messages arrive
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

  // Load chat sessions on mount AND restore last chat from localStorage
  useEffect(() => {
    loadChatSessions();
    restoreLastChat();
  }, []);

  // Save current chat to localStorage whenever it changes
  useEffect(() => {
    if (currentChat && currentChat.id) {
      localStorage.setItem('comenius_last_chat_id', currentChat.id);
      if (messages.length > 0) {
        localStorage.setItem('comenius_last_chat_messages', JSON.stringify(messages));
      }
    }
  }, [currentChat, messages]);

  const restoreLastChat = async () => {
    const savedChatId = localStorage.getItem('comenius_last_chat_id');
    const savedMessages = localStorage.getItem('comenius_last_chat_messages');
    
    if (savedChatId && savedMessages) {
      try {
        // Cargar el chat completo desde el servidor
        const response = await api.get(`/ai/chat/${savedChatId}/`);
        setCurrentChat(response.data);
        setMessages(response.data.messages || []);
      } catch (error) {
        // Si falla (chat eliminado o expirado), limpiar localStorage
        console.error('Error restoring chat:', error);
        localStorage.removeItem('comenius_last_chat_id');
        localStorage.removeItem('comenius_last_chat_messages');
        // No restaurar nada si el chat no existe en el servidor
      }
    }
  };

  const loadChatSessions = async () => {
    try {
      const response = await api.get('/ai/chat/');
      setChatSessions(response.data);
    } catch (error) {
      console.error('Error loading chat sessions:', error);
    }
  };

  const loadChatMessages = async (chatId) => {
    try {
      const response = await api.get(`/ai/chat/${chatId}/`);
      setCurrentChat(response.data);
      setMessages(response.data.messages || []);
    } catch (error) {
      console.error('Error loading chat messages:', error);
    }
  };

  const handleSendMessage = async (messageText) => {
    if (!messageText.trim()) return;

    setIsLoading(true);

    try {
      // If no current chat, start a new one
      if (!currentChat) {
        const response = await api.post('/ai/chat/start_new/', {
          message: messageText
        });

        // Backend returns { chat: {...}, success: true }
        setCurrentChat(response.data.chat);
        setMessages(response.data.chat.messages || []);
        await loadChatSessions(); // Refresh sidebar
      } else {
        // Send message to existing chat
        const response = await api.post(`/ai/chat/${currentChat.id}/send_message/`, {
          message: messageText
        });

        // Append both user and assistant messages
        setMessages(prev => [
          ...prev,
          response.data.user_message,
          response.data.assistant_message
        ]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      alert('Error al enviar el mensaje. Por favor intenta de nuevo.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = () => {
    setCurrentChat(null);
    setMessages([]);
    // Limpiar persistencia del localStorage
    localStorage.removeItem('comenius_last_chat_id');
    localStorage.removeItem('comenius_last_chat_messages');
  };

  const handleSelectChat = (chatId) => {
    loadChatMessages(chatId);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <ChatSidebar
        chatSessions={chatSessions}
        currentChatId={currentChat?.id}
        onSelectChat={handleSelectChat}
        onNewChat={handleNewChat}
        isOpen={isSidebarOpen}
        onToggle={() => setIsSidebarOpen(!isSidebarOpen)}
      />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white border-b px-6 py-4 shadow-sm">
          <div className="flex items-center">
            <img src={comeniusLogo} alt="ComeniusAI" className="w-10 h-10 mr-3" />
            <div>
              <h1 className="text-2xl font-bold text-gray-800">
                ComeniusAI
              </h1>
              <p className="text-sm text-gray-600 mt-1">
                Asistente educativo basado en evidencia científica
              </p>
            </div>
          </div>
        </div>

        {/* Messages Container */}
        <div className="flex-1 overflow-y-auto px-6 py-6">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <img src={comeniusLogo} alt="ComeniusAI" className="w-24 h-24 mb-4" />
              <h2 className="text-2xl font-bold text-gray-800 mb-4">
                ¡Hola! Soy ComeniusAI, tu asistente educativo basado en evidencia.
              </h2>
              <p className="text-gray-700 max-w-md mb-2">
                ¿Tienes dudas sobre <strong>metodologías, evaluación, motivación</strong> o <strong>gestión de aula</strong>?
              </p>
              <p className="text-gray-600 max-w-md mb-6">
                Te daré respuestas rápidas apoyadas en investigaciones científicas reales.
              </p>
              <div className="mt-6 text-left bg-white p-6 rounded-lg shadow-sm max-w-md border border-gray-200">
                <p className="font-semibold text-gray-700 mb-3">💡 ¿En qué puedo ayudarte hoy?</p>
                <p className="text-sm text-gray-500 mb-3">Ejemplos de preguntas:</p>
                <ul className="text-sm text-gray-600 space-y-2">
                  <li>• ¿Qué dice la evidencia sobre el aprendizaje cooperativo?</li>
                  <li>• ¿Cómo puedo mejorar la comprensión lectora en primaria?</li>
                  <li>• ¿Qué estrategias funcionan para motivar a estudiantes?</li>
                  <li>• Evidencia sobre el uso de gamificación en el aula</li>
                </ul>
              </div>
            </div>
          ) : (
            <div className="max-w-4xl mx-auto space-y-4">
              {messages.map((msg, index) => (
                <ChatBubble key={index} message={msg} />
              ))}
              {isLoading && (
                <div className="flex items-center space-x-2 text-gray-500">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                  <span className="text-sm">🔍 Buscando artículos científicos...</span>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Message Input */}
        <MessageInput onSendMessage={handleSendMessage} disabled={isLoading} />
      </div>
    </div>
  );
}
