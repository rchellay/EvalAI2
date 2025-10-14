import { Navigate } from 'react-router-dom';
import { isValid } from './token';
import { useEffect, useState } from 'react';

export default function ProtectedRoute({ children }) {
  const [ok, setOk] = useState(null);
  useEffect(() => {
    const token = localStorage.getItem('token');
    const valid = isValid(token);
    console.debug('[ProtectedRoute] token?', !!token, 'valid?', valid, 'path:', window.location.pathname);
    setOk(valid);
  }, []);
  if (ok === null) return <div style={{padding:'3rem', textAlign:'center'}}>Verificando sesión...</div>;
  if (!ok) {
    console.debug('[ProtectedRoute] not valid redirecting');
    return <Navigate to="/" replace />;
  }
  return children;
}
