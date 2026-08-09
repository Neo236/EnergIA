import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// El front habla con la API en el MISMO ORIGEN (/api/v1/...). En la VM eso
// lo resuelve Caddy; acá lo resuelve este proxy, para que el código no
// necesite una URL base ni condicionales por entorno.
//
// VITE_API_DESTINO permite apuntar el proxy a donde haga falta:
//   - sin definir            → backend local en :8080
//   - http://127.0.0.1:8082  → túnel SSH contra el backend de la VM
//     ssh -N -L 8082:127.0.0.1:8082 energiai
//
// Se lee con loadEnv y no con process.env: este archivo corre en Node antes
// de que Vite cargue los .env, así que process.env NO contiene las
// variables del archivo — solo las de la terminal.
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const destinoApi = env.VITE_API_DESTINO || 'http://127.0.0.1:8080'
  const alBackend = { target: destinoApi, changeOrigin: true }

  return {
    plugins: [react()],
    server: {
      port: 5173,
      proxy: {
        '/api': alBackend,
        // Mismas rutas que rutea Caddy en la VM, para que Swagger y el
        // healthcheck también funcionen durante el desarrollo.
        '/swagger-ui': alBackend,
        '/v3/api-docs': alBackend,
        '/actuator': alBackend,
      },
    },
    build: {
      outDir: 'dist',
      sourcemap: true,
    },
  }
})
