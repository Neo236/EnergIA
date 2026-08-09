# Prototipo estático — P-01 / P-02 (archivado)

> 📦 **Esto no es la aplicación.** Es la primera implementación del front-end,
> en HTML, CSS y JavaScript puros, anterior a la migración a Vite + React +
> TypeScript. Se conserva como referencia de cómo se resolvió cada control
> sin framework y como registro de la etapa. **No se construye ni se
> despliega** — está excluido del contexto de Docker en `.dockerignore`.

La aplicación viva está en `frontend/src/`. Ver [`../README.md`](../README.md).

## Para qué sirve todavía

- **Referencia de implementación**: el stepper, el deslizador, el interruptor
  y el desplegable están resueltos acá con DOM plano. Si alguna vez hay que
  entender por qué un control se comporta de cierta forma, el original está
  a la vista.
- **Registro del punto de partida**: el estado exacto que se desplegó por
  primera vez en la VM de OCI y se demostró al equipo.

## Cómo verlo

Se abre `index.html` en el navegador. No necesita servidor, ni build, ni
dependencias — que era justamente su razón de ser.

## Estructura

| Archivo | Qué contiene |
|---|---|
| `index.html` | Marcado completo de P-01 y P-02 |
| `css/tokens.css` | Neutrales del wireframe y paleta temporal |
| `css/app.css` | Estilos de componentes y responsive |
| `js/schema.js` | Contrato V1.2: campos, rangos, enums y defaults |
| `js/api.js` | Transporte con mock y modo real |
| `js/app.js` | Estado y render de los ocho estados de pantalla |

## Qué se llevó la migración

Los estilos pasaron casi sin cambios a `src/styles/`. `schema.js` se convirtió
en `src/lib/contrato.ts` con tipos, y `api.js` se separó en `src/lib/api.ts`
(transporte) y `src/lib/mock.ts` (simulación). La lógica de `app.js` se
repartió entre las páginas y los componentes.
