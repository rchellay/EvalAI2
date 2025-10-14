import { jwtDecode } from 'jwt-decode';

export function parseToken(token) {
  try {
    const payload = jwtDecode(token);
    const expMs = payload.exp ? payload.exp * 1000 : 0;
    const expired = expMs ? Date.now() > expMs : true;
    return { payload, expired };
  } catch {
    return { payload: null, expired: true };
  }
}

export function isValid(token) {
  if (!token) return false;
  const { expired } = parseToken(token);
  return !expired;
}
