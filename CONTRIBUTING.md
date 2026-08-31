# Cómo contribuir

## Flujo de ramas

```
main ← feature/mi-cambio
```

`main` está protegida: **no se pushea directo**. Todo entra por Pull Request con
la integración continua en verde.

```bash
git switch -c feature/lo-que-hago
# ... trabajás, commiteás ...
git push -u origin feature/lo-que-hago
gh pr create
```

**Nombres de rama:** `<tipo>/<tema-en-kebab-case>` — `feature/` para
funcionalidad nueva, `fix/` para correcciones, `chore/` para mantenimiento. El
tema describe el cambio, no a la persona: `feature/filtro-historial`, no
`feature/juan-2`.

> Durante el hackathon el flujo tenía una capa intermedia (`develop`) porque cada
> rama disparaba un despliegue a un ambiente distinto. Ya no hay staging, así que
> esa capa se retiró: agregaba ceremonia sin cumplir ninguna función.

## Mensajes de commit

```
tipo(alcance): descripción en minúscula

Por qué hacía falta este cambio y qué problema resuelve. Si hay una
decisión no obvia, dejala explicada acá — el diff ya muestra el qué.
```

Los mensajes del historial son largos a propósito: explican el porqué, no el
qué. Es la vara del proyecto.

**No agregues trailers de coautoría de asistentes de IA.** Usalos todo lo que
quieras para trabajar; simplemente no van en el historial.

## Antes de abrir el PR

```bash
cd backend/analisis-energetico-api && ./mvnw test   # backend
npm --prefix frontend test                          # frontend
npm --prefix frontend run build                     # que compile
cd data-science/raw && python -m pytest             # ml-service
```

La integración continua corre lo mismo, pero descubrirlo en tu máquina es más
rápido que esperar el pipeline.

Si el cambio se ve en el navegador, miralo en el navegador. Que compile no es
que funcione.

## Convenciones de código

- **Todo en español**: clases, métodos, variables, comentarios, documentación.
  `AnalisisEnergeticoService`, no `EnergyAnalysisService`.
- **Los comentarios explican por qué**, no qué hace la línea de abajo.
- El estilo de cada área sigue el del código que la rodea. Antes de introducir un
  patrón nuevo, fijate cómo se resolvió algo parecido en el repositorio.

## Antes de cambiar algo que parece un error

[`AGENTS.md`](./AGENTS.md) lista varias decisiones deliberadas que **parecen**
errores: por qué el modelo entrenado está versionado, por qué el bind del proxy
no es `0.0.0.0`, por qué la tipografía no viene de Google Fonts, por qué no hay
endpoint de borrado. Léelo antes de "arreglar" alguna.

## Levantar el proyecto

Está todo en [`docs/DESPLIEGUE.md`](./docs/DESPLIEGUE.md). El camino corto:

```bash
docker compose up --build -d   # → http://localhost:8088
```
