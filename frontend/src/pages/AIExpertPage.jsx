import { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import ChatBubble from '../components/chat/ChatBubble';
import MessageInput from '../components/chat/MessageInput';
import ChatSidebar from '../components/chat/ChatSidebar';

const API_URL = import.meta.env.VITE_API_URL || 'https://evalai2.onrender.com';

export default function AIExpertPage() {
  const { user } = useAuth();
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

  // Load chat sessions on mount
  useEffect(() => {
    loadChatSessions();
  }, []);

  const loadChatSessions = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/api/ai/chat/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setChatSessions(response.data);
    } catch (error) {
      console.error('Error loading chat sessions:', error);
    }
  };

  const loadChatMessages = async (chatId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/api/ai/chat/${chatId}/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
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
      const token = localStorage.getItem('token');

      // If no current chat, start a new one
      if (!currentChat) {
        const response = await axios.post(
          `${API_URL}/api/ai/chat/start_new/`,
          { message: messageText },
          { headers: { Authorization: `Bearer ${token}` } }
        );

        setCurrentChat(response.data);
        setMessages(response.data.messages || []);
        await loadChatSessions(); // Refresh sidebar
      } else {
        // Send message to existing chat
        const response = await axios.post(
          `${API_URL}/api/ai/chat/${currentChat.id}/send_message/`,
          { message: messageText },
          { headers: { Authorization: `Bearer ${token}` } }
        );

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
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-800">
                🎓 Asistente de Investigación Educativa
              </h1>
              <p className="text-sm text-gray-600 mt-1">
                Respuestas basadas en evidencia científica real
              </p>
            </div>
            <button
              onClick={handleNewChat}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              + Nueva Conversación
            </button>
          </div>
        </div>

        {/* Messages Container */}
        <div className="flex-1 overflow-y-auto px-6 py-6">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="text-6xl mb-4">🔬</div>
              <h2 className="text-2xl font-semibold text-gray-700 mb-2">
                ¡Hola, {user?.first_name}!
              </h2>
              <p className="text-gray-600 max-w-md">
                Pregúntame sobre investigación educativa. Buscaré estudios científicos reales
                de Semantic Scholar y OpenAlex para darte respuestas respaldadas por evidencia.
              </p>
              <div className="mt-6 text-left bg-white p-6 rounded-lg shadow-sm max-w-md">
                <p className="font-semibold text-gray-700 mb-2">Ejemplos de preguntas:</p>
                <ul className="text-sm text-gray-600 space-y-2">
                  <li>• ¿Qué dice la evidencia sobre el aprendizaje cooperativo?</li>
                  <li>• ¿Cómo puedo mejorar la comprensión lectora en primaria?</li>
                  <li>• ¿Qué estrategias funcionan para motivar a estudiantes desmotivados?</li>
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
