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
          
          <div style={{margin: '1.5rem 0', textAlign: 'center', color: '#64748b'}}>
            <span style={{position: 'relative', padding: '0 1rem', background: '#1e293b'}}>
              <span style={{position: 'absolute', top: '50%', left: 0, right: 0, height: '1px', background: '#334155', zIndex: -1}}></span>
              o
            </span>
          </div>
          
          <button 
            type="button"
            onClick={() => window.location.href = `${import.meta.env.VITE_API_URL}/accounts/google/login/`}
            disabled={loading}
            style={{
              width: '100%',
              padding: '0.75rem',
              background: 'white',
              color: '#1f2937',
              border: '1px solid #d1d5db',
              borderRadius: '0.5rem',
              fontSize: '1rem',
              fontWeight: 500,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.75rem',
              transition: 'all 0.2s'
            }}
            onMouseOver={(e) => e.currentTarget.style.background = '#f9fafb'}
            onMouseOut={(e) => e.currentTarget.style.background = 'white'}
          >
            <svg width="18" height="18" viewBox="0 0 18 18">
              <path fill="#4285F4" d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.717v2.258h2.908c1.702-1.567 2.684-3.875 2.684-6.615z"/>
              <path fill="#34A853" d="M9 18c2.43 0 4.467-.806 5.956-2.184l-2.908-2.258c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332C2.438 15.983 5.482 18 9 18z"/>
              <path fill="#FBBC05" d="M3.964 10.707c-.18-.54-.282-1.117-.282-1.707 0-.593.102-1.17.282-1.709V4.958H.957C.347 6.173 0 7.548 0 9s.348 2.827.957 4.042l3.007-2.335z"/>
              <path fill="#EA4335" d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0 5.482 0 2.438 2.017.957 4.958L3.964 7.29C4.672 5.163 6.656 3.58 9 3.58z"/>
            </svg>
            Continuar con Google
          </button>
          
          <div id="googleBtn" style={{display:'none'}} />
        </form>
        <p className="subtle" style={{marginTop:'1.4rem'}}>Demo: registra un usuario vía script backend y pruébalo aquí.</p>
      </div>
    </div>
  );
}
