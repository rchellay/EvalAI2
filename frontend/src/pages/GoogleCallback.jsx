import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';

export default function GoogleCallback() {
  const navigate = useNavigate();

  useEffect(() => {
    // Extraer el token de la URL
    const params = new URLSearchParams(window.location.search);
    const token = params.get('token');

    if (token) {
      // Guardar el token
      localStorage.setItem('token', token);
      toast.success('¡Inicio de sesión con Google exitoso!');
      
      // Redirigir al dashboard
      navigate('/dashboard', { replace: true });
    } else {
      // Si no hay token, hubo un error
      toast.error('Error al iniciar sesión con Google');
      navigate('/', { replace: true });
    }
  }, [navigate]);

  return (
    <div className="center-page">
      <div className="glass-card" style={{ textAlign: 'center' }}>
        <h2>Procesando inicio de sesión con Google...</h2>
        <p style={{ marginTop: '1rem', color: '#64748b' }}>
          Serás redirigido en un momento.
        </p>
      </div>
    </div>
  );
}
