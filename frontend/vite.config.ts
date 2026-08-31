// defineConfig sale de 'vitest/config' (no de 'vite') para que TypeScript
// reconozca el campo `test` de abajo — es un re-export que fusiona los tipos
// de Vite con los de Vitest, así no hace falta duplicar config en otro archivo.
// loadEnv sigue viniendo de 'vite': 'vitest/config' no lo reexporta.
import { defineConfig } from 'vitest/config'
import { loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// El front habla con la API en el MISMO ORIGEN (/api/v1/...). En la VM eso
// lo resuelve Caddy; acá lo resuelve este proxy, para que el código no
// necesite una URL base ni condicionales por entorno.
//
// VITE_API_DESTINO permite apuntar el proxy a donde haga falta:
//   - sin definir            → backend local en :8080
//   - http://127.0.0.1:8082  → túnel SSH contra el backend de la VM
//     ssh -N -L 8082:127.0.0.1:8082 energia
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
    test: {
      environment: 'jsdom',
      // Fija la zona horaria del proceso de test a UTC: fechaLegible/
      // fechaRelativa usan getters locales (getHours, getDate) a propósito
      // (ver formato.ts), así que sin esto las aserciones dependerían de en
      // qué zona horaria corra quien ejecute los tests o el CI.
      env: { TZ: 'UTC' },
    },
  }
})
