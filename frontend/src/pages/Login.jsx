import { useState, useEffect, useCallback } from "react";
import { isValid } from '../auth/token';
import api from '../lib/axios';
import { useNavigate } from "react-router-dom";
import { toast } from 'react-hot-toast';

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [mode, setMode] = useState('login');
  const [email, setEmail] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const t = localStorage.getItem('token');
    console.debug('[Login] initial token present?', !!t, 'valid?', isValid(t));
    if (isValid(t)) {
      navigate('/dashboard', { replace:true });
      setTimeout(()=>{
        if (window.location.pathname === '/') {
          console.debug('[Login] navigate fallback triggered');
          window.location.assign('/dashboard');
        }
      }, 150);
    }
  }, [navigate]);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await api.post("/auth/login", { username, password });
      localStorage.setItem("token", res.data.access_token);
      console.debug('[Login] login success, navigating to /dashboard');
	navigate("/dashboard", { replace:true });
      setTimeout(()=>{
        if (window.location.pathname === '/') {
          console.debug('[Login] fallback after classic login');
          window.location.assign('/dashboard');
        }
      }, 150);
      toast.success('Bienvenido');
    } catch (err) {
      setError("Credenciales inválidas o servidor no disponible");
      toast.error('Error al iniciar sesión');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true); setError(null);
    try {
      await api.post('/auth/register', { username, email, password });
      toast.success('Usuario registrado');
      setMode('login');
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Error registrando');
      setError(e.response?.data?.detail || 'Error registrando');
    } finally { setLoading(false); }
  };

  const handleGoogleCredential = useCallback(async (response) => {
    try {
      const id_token = response.credential;
      const res = await api.post('/auth/google', { id_token });
      localStorage.setItem('token', res.data.access_token);
      toast.success('Login Google OK');
      console.debug('[Login] google login success navigate');
	navigate('/dashboard', { replace:true });
      setTimeout(()=>{
        if (window.location.pathname === '/') {
          console.debug('[Login] fallback after google login');
          window.location.assign('/dashboard');
        }
      }, 150);
    } catch (e) {
      toast.error('Error con Google');
    }
  }, [navigate]);

  useEffect(() => {
    const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;
    if (window.google && clientId) {
      window.google.accounts.id.initialize({
        client_id: clientId,
        callback: handleGoogleCredential,
        ux_mode: 'popup'
      });
      const el = document.getElementById('googleBtn');
      if (el) {
        window.google.accounts.id.renderButton(el, { theme: 'outline', size: 'large', shape: 'pill', text: 'signin_with', width: 260 });
      }
    }
  }, [handleGoogleCredential]);

  return (
    <div className="center-page">
      <div className="glass-card">
        <div style={{display:'flex', gap:'1rem', marginBottom:'1rem'}}>
          <button type="button" className={`btn-primary ${mode==='login'?'':'opacity-60'}`} style={{flex:1}} onClick={()=>setMode('login')} disabled={loading}>Login</button>
          <button type="button" className={`btn-primary ${mode==='register'?'':'opacity-60'}`} style={{flex:1}} onClick={()=>setMode('register')} disabled={loading}>Registro</button>
        </div>
        <h1>{mode==='login' ? 'Iniciar Sesión' : 'Crear Cuenta'}</h1>
        <form className="auth-form" onSubmit={mode==='login'?handleLogin:handleRegister}>
          <div className="input-group">
            <label>Usuario</label>
            <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} placeholder="tu_usuario" required />
          </div>
          {mode==='register' && (
            <div className="input-group">
              <label>Email</label>
              <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="correo@ejemplo.com" required />
            </div>
          )}
          <div className="input-group">
            <label>Contraseña</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="********" required />
          </div>
          {error && <div className="error-box">{error}</div>}
          <button className="btn-primary" type="submit" disabled={loading}>{loading ? '...' : (mode==='login'?'Entrar':'Registrar')}</button>
          <div id="googleBtn" style={{display:'flex', justifyContent:'center'}} />
        </form>
        <p className="subtle" style={{marginTop:'1.4rem'}}>Demo: registra un usuario vía script backend y pruébalo aquí.</p>
      </div>
    </div>
  );
}
