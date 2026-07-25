# ⚙️ Gobernanza de Git, Protección de Ramas y CI/CD – EnergiAI

Este documento registra la arquitectura de ramas, las **reglas de protección de ramas activas en GitHub** y la configuración del pipeline de **Integración Continua (CI)** del repositorio **G9-LATAM-TEAM-09**.

---

## 🔀 1. Arquitectura de Ramas (GitFlow Simplificado)

El repositorio sigue un modelo de desarrollo colaborativo estructurado en tres niveles:

| Rama | Propósito | Reglas de Acceso |
|------|-----------|------------------|
| `main` | Rama de Producción y entregables estables probados. | **Protegida**. Solo recibe merges vía Pull Request aprobados desde `develop`. |
| `develop` | Rama principal de integración y desarrollo activo. | **Protegida**. Recibe merges vía Pull Request desde ramas `feature/*`. |
| `feature/*` | Ramas individuales para nuevas características, correcciones o documentación. | Libres para los desarrolladores. Nacen de `develop` y se integran mediante PR. |

---

## 🛡️ 2. Reglas de Protección de Ramas (Configuradas mediante GitHub Rulesets)

En la sección **Settings > Rules > Rulesets** del repositorio en GitHub, se encuentra activo el Ruleset oficial del proyecto:

### 🟢 Ruleset: `Proteger Main` (Estado: Active)
- **Ramas Objetivo (*Target Branches*)**: Aplica a **`main`** y **`develop`**.
- **Reglas Configuradas**:
  - ✅ **Require a pull request before merging**: Exige que todos los cambios se envíen mediante Pull Request (Requiere mínimo **1 aprobación** de revisión).
  - ✅ **Restrict deletions**: Impide la eliminación de las ramas objetivo.
  - ✅ **Require status checks to pass before merging**: Exige que el pipeline de CI (`backend-ci` y `docker-ci`) pase exitosamente antes de autorizar el merge.
  - ✅ **Bypass List**: Vacía (ningún usuario puede saltarse las reglas de integración).

---

## 🚀 3. Integración Continua (CI Workflow)

El repositorio cuenta con un pipeline de **GitHub Actions** automatizado definido en [`.github/workflows/ci.yml`](../.github/workflows/ci.yml).

### Disparadores (*Triggers*)
- Se ejecuta automáticamente ante cada **Push** o **Pull Request** hacia las ramas `main` y `develop`.

### Trabajos (*Jobs*)
1. **`backend-ci` (Spring Boot & Java 17)**:
   - Entorno: `ubuntu-latest` con JDK 17 (Temurin).
   - Utiliza caché automatizado de dependencias Maven (`.m2`).
   - Ejecuta `./mvnw clean test` para validar las pruebas unitarias y de integración del backend.
   - Ejecuta `./mvnw package -DskipTests` para verificar el empaquetado del artefacto `.jar`.
2. **`docker-ci` (Orquestación Containerizada)**:
   - Entorno: `ubuntu-latest`.
   - Ejecuta `docker compose config` para validar la sintaxis, variables y contextos del archivo `docker-compose.yml`.

---

## ⚖️ 4. Licencia del Proyecto

El proyecto está licenciado bajo la **Licencia MIT**.
- **Archivo de Licencia**: [`LICENSE`](../LICENSE) en la raíz del repositorio.
- **Declaración en Maven**: Etiqueta `<licenses>` configurada en [`pom.xml`](../backend/analisis-energetico-api/pom.xml).

---

## 🔄 5. Protocolo de Sincronización entre `develop` y `main`

Para mantener la consistencia y sincronización entre `develop` y `main` respetando la protección activa:

1. Finalizada la iteración/semana, se verifica que todos los PRs de `feature/*` estén integrados en `develop` y con la suite de CI aprobada.
2. Se abre un **Pull Request en GitHub**: `base: main` ⬅️ `compare: develop`.
3. El responsable revisa los cambios y verifica el paso del pipeline de CI.
4. Se autoriza el merge (*Create a merge commit* o *Rebase and merge*).
5. Ambas ramas quedan alineadas y en estado verde.
