import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: true, // Forzar puerto 5173, fallar si está ocupado
    host: true,
  },
});
