// frontend/src/components/StudentAvatar.jsx
import { useMemo } from 'react';

/**
 * Componente reutilizable para mostrar avatares de estudiantes
 * Soporta: inicial, emoji, imagen
 */
const StudentAvatar = ({ student, size = 'md', className = '' }) => {
  // Tamaños predefinidos
  const sizeClasses = {
    sm: 'w-8 h-8 text-sm',
    md: 'w-12 h-12 text-xl',
    lg: 'w-16 h-16 text-2xl',
    xl: 'w-24 h-24 text-4xl',
    '2xl': 'w-32 h-32 text-5xl'
  };

  const sizeClass = sizeClasses[size] || sizeClasses.md;

  const avatarContent = useMemo(() => {
    // Si tiene avatar_type e información
    if (student.avatar_type && student.avatar_value) {
      // Tipo imagen (base64 o URL)
      if (student.avatar_type === 'image') {
        return (
          <img 
            src={student.avatar_value} 
            alt={student.name || student.username || 'Avatar'} 
            className={`${sizeClass} rounded-full object-cover`}
          />
        );
      }

      // Tipo emoji
      if (student.avatar_type === 'emoji') {
        try {
          const avatar = JSON.parse(student.avatar_value);
          const emojiSize = {
            sm: 'text-xs',
            md: 'text-lg',
            lg: 'text-2xl',
            xl: 'text-4xl',
            '2xl': 'text-6xl'
          }[size] || 'text-lg';

          return (
            <div className={`${sizeClass} rounded-full bg-gradient-to-br ${avatar.color} flex items-center justify-center`}>
              <span className={emojiSize}>{avatar.emoji}</span>
            </div>
          );
        } catch (e) {
          // Fallback a inicial
        }
      }
    }

    // Default: Inicial (letra del nombre)
    const initial = (student.name || student.username || '?').charAt(0).toUpperCase();
    return (
      <div className={`${sizeClass} rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center text-blue-600 dark:text-blue-300 font-bold`}>
        {initial}
      </div>
    );
  }, [student, size, sizeClass]);

  return (
    <div className={className}>
      {avatarContent}
    </div>
  );
};

export default StudentAvatar;
