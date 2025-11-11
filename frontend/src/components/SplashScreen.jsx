import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { SkipForward } from 'lucide-react';

export default function SplashScreen({ onComplete }) {
  const [shouldShow, setShouldShow] = useState(false);
  const [isSkipping, setIsSkipping] = useState(false);

  useEffect(() => {
    // Verificar si ya se mostró el splash (o forzar con ?splash=1)
    const hasSeenSplash = localStorage.getItem('hasSeenSplash');
    const forceSplash = new URLSearchParams(window.location.search).get('splash');
    
    if (!hasSeenSplash || forceSplash === '1') {
      setShouldShow(true);
      
      // ELIMINADO: Auto-skip después de 8 segundos
      // El video ahora se reproduce completo sin saltar automáticamente
    } else {
      onComplete();
    }
  }, [onComplete]);

  const handleComplete = () => {
    setIsSkipping(true);
    localStorage.setItem('hasSeenSplash', 'true');
    
    // Pequeña animación antes de completar
    setTimeout(() => {
      onComplete();
    }, 500);
  };

  if (!shouldShow) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: isSkipping ? 0 : 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.5 }}
        className="fixed inset-0 z-[9999] flex items-center justify-center bg-slate-900"
      >
        {/* Video de fondo */}
        <video
          autoPlay
          muted
          playsInline
          className="absolute inset-0 w-full h-full object-cover opacity-60"
          onEnded={handleComplete}
        >
          <source src="/splash-video.mp4" type="video/mp4" />
          <source src="/splash-video.webm" type="video/webm" />
        </video>

        {/* Overlay oscuro */}
        <div className="absolute inset-0 bg-gradient-to-b from-slate-900/50 via-slate-900/30 to-slate-900/70" />

        {/* Contenido principal */}
        <div className="relative z-10 flex flex-col items-center justify-center px-4">
          {/* Logo principal - SIN título duplicado */}
          <motion.div
            initial={{ scale: 0.5, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="mb-8"
          >
            <img
              src="/evalai-logo.png"
              alt="EvalAI Logo"
              className="w-48 h-48 md:w-64 md:h-64 object-contain drop-shadow-2xl"
              onError={(e) => {
                // Fallback si no existe el logo
                e.target.style.display = 'none';
              }}
            />
          </motion.div>

          {/* TÍTULO ELIMINADO: ya está en el logo */}
          
          {/* Barra de progreso (basada en duración del video) */}
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: '100%' }}
            transition={{ duration: 15, ease: "linear" }} // Ajusta según duración de tu video
            className="absolute bottom-0 left-0 h-1 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500"
          />
        </div>

        {/* Botón Skip */}
        <motion.button
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1 }}
          onClick={handleComplete}
          className="absolute bottom-8 right-8 z-20 flex items-center gap-2 px-6 py-3 
                   bg-white/10 hover:bg-white/20 backdrop-blur-sm 
                   text-white rounded-full border border-white/20
                   transition-all duration-300 group"
        >
          <span className="font-medium">Saltar</span>
          <SkipForward size={20} className="group-hover:translate-x-1 transition-transform" />
        </motion.button>

        {/* Texto informativo inferior */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 2 }}
          className="absolute bottom-8 left-8 text-slate-400 text-sm"
        >
          Cargando experiencia...
        </motion.p>
      </motion.div>
    </AnimatePresence>
  );
}
