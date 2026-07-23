# EnergiAI

## Hackathon ONE G9 LATAM

**Sector:** Sostenibilidad, Energía y Casas Inteligentes  
**Estado:** En desarrollo  
**Etapa:** Semana 1  
**Actualización:** 21 de julio de 2026

---

## 1. Descripción

EnergiAI es una solución inteligente para analizar el consumo eléctrico de viviendas y pequeños establecimientos.

Busca transformar datos básicos de consumo en información útil para:

- Comprender el perfil energético.
- Detectar desperdicios.
- Estimar el costo mensual.
- Recibir recomendaciones.
- Promover hábitos sostenibles.

La solución clasificará cada caso como **Eficiente**, **Moderado** o **Ineficiente**, y entregará los resultados mediante una API REST en formato JSON.

---

## 2. Problema

Muchas personas reciben facturas elevadas, pero no saben qué hábitos, horarios o equipos explican su consumo.

Las principales dificultades son:

- Poca visibilidad sobre los patrones de uso.
- Dificultad para interpretar el consumo mensual.
- Uso intensivo de equipos en horarios punta.
- Falta de recomendaciones personalizadas.
- Ausencia de herramientas simples para estimar ahorro.

---

## 3. Objetivo

Desarrollar un MVP capaz de analizar patrones de consumo eléctrico, clasificar el perfil energético, estimar costos y generar recomendaciones para apoyar decisiones de ahorro y sostenibilidad.

Objetivos específicos:

- Construir y analizar un dataset energético.
- Definir criterios de eficiencia.
- Entrenar y evaluar modelos supervisados.
- Informar clasificación y probabilidad.
- Estimar el costo mensual.
- Generar recomendaciones.
- Publicar resultados mediante una API REST.
- Integrar al menos un servicio OCI.
- Documentar arquitectura, endpoints y resultados.

---

## 4. Alcance del MVP

El MVP incluirá:

- Ingreso y validación de datos.
- Clasificación energética.
- Probabilidad asociada.
- Estimación financiera.
- Recomendaciones.
- API REST y respuestas JSON.
- Manejo de errores.
- Swagger/OpenAPI.
- Modelo entrenado y serializado.
- Notebook de Ciencia de Datos.
- Integración con OCI.
- Tres casos de uso.

Opcionales, solo después de completar el MVP:

- Interfaz web.
- Dashboard.
- Historial.
- Comparación entre períodos.
- Procesamiento CSV.
- Simulación de ahorro.
- Alertas.
- Ranking energético.

---

## 5. Datos de entrada

Campos iniciales:

- `consumo_kwh`
- `uso_horario_pico`
- `cantidad_equipos`
- `tipo_inmueble`
- `horas_alto_consumo`

Ejemplo:

```json
{
  "consumo_kwh": 420,
  "uso_horario_pico": true,
  "cantidad_equipos": 10,
  "tipo_inmueble": "Casa",
  "horas_alto_consumo": 8
}
```

---

## 6. Salida esperada

```json
{
  "categoria": "Ineficiente",
  "probabilidad": 0.81,
  "costo_estimado_mensual": 315.00,
  "recomendaciones": [
    "Reducir el uso de equipos durante horarios pico",
    "Evaluar los equipos con mayor consumo",
    "Distribuir las actividades intensivas durante el día"
  ]
}
```

---

## 7. Estimación financiera

Se utilizará como referencia una tarifa de **0,75 por kWh**.

```text
Costo mensual = consumo_kwh × tarifa_kwh
```

Ejemplo:

```text
420 × 0,75 = 315,00
```

---

## 8. Ciencia de Datos

El trabajo incluirá construcción, limpieza y exploración del dataset; definición de categorías; ingeniería de variables; entrenamiento, evaluación, selección y serialización del modelo.

Modelos iniciales:

- Regresión Logística.
- Árbol de Decisión.
- Random Forest.

Métricas:

- F1 macro.
- Exactitud.
- Precisión.
- Recall.
- Balanced accuracy.
- Matriz de confusión.

---

## 9. Notebook

El proyecto incluirá un archivo `.ipynb` con carga y exploración del dataset, estadísticas, limpieza, visualizaciones, transformaciones, entrenamiento, evaluación, conclusiones y serialización.

---

## 10. Back-End

Tecnologías propuestas:

- Java y Spring Boot.
- Maven.
- Bean Validation.
- Swagger/OpenAPI.
- JUnit.
- Docker.

Endpoints:

```http
POST /api/v1/analisis-energetico
GET /api/v1/analisis/{id}
GET /api/v1/health
```

La API validará datos, clasificará el perfil, calculará costos, generará recomendaciones y devolverá códigos HTTP adecuados.

Ejemplo de error:

```json
{
  "status": 400,
  "error": "Datos de entrada inválidos",
  "message": "El consumo_kwh debe ser mayor que cero"
}
```

---

## 11. Arquitectura preliminar

```text
Usuario o Front-End
        |
        v
API REST Spring Boot
        |
        v
Validación y preprocesamiento
        |
        v
Modelo de Ciencia de Datos
        |
        v
Clasificación y probabilidad
        |
        +----------------------+
        |                      |
        v                      v
Recomendaciones          Cálculo financiero
        |                      |
        +----------+-----------+
                   |
                   v
             Respuesta JSON
                   |
                   v
                 OCI
```

La integración Python-Java se resolverá mediante ONNX o un microservicio FastAPI, según estabilidad y facilidad de despliegue.

---

## 12. Uso de OCI

Servicios considerados:

- **OCI Object Storage:** dataset, modelo, métricas y evidencias.
- **OCI Compute:** despliegue de la API y ejecución del contenedor.
- **OCI Functions:** procesamiento complementario, si resulta necesario.

---

## 13. Recomendaciones

Las recomendaciones usarán reglas explicables, por ejemplo: reducir uso en horarios punta, desconectar equipos en espera, revisar equipos antiguos, disminuir horas de alto consumo y mantener hábitos eficientes.

---

## 14. Equipo

- **Marco Antonio Soto Bobadilla:** Project Manager.
- **Constanza Albornoz:** Data Analyst.
- **Nahuel Rosas:** Data Scientist.
- **Randy Roco Mellado:** Data Engineer.
- **Leandro Ariel Moreno:** Back-End Developer.
- **Alan Federico Cabrera:** Back-End Developer.
- **Lautaro Sebastián Mambrin:** Full-Stack Developer.
- **Sergio Villena:** Software Engineer.

---

## 15. Metodología

El equipo aprobó trabajar con **Scrumban**.

Dinámica:

- Sprint Planning los lunes.
- Seguimiento mediante Discord y Trello.
- Control de integración los miércoles.
- Sprint Demo los jueves.
- Retrospectiva breve.

Herramientas:

- **Trello:** gestión de tareas.
- **GitHub:** código, notebooks y documentación.
- **Discord:** comunicación.
- **OCI:** infraestructura y despliegue.

Flujo:

```text
Sprint actual
→ En desarrollo
→ En revisión
→ En pruebas
→ Terminado
```

---

## 16. Estado actual

### Completado

- Equipo conformado.
- Disponibilidades revisadas.
- Horario común definido.
- Metodología Scrumban aprobada.
- Repositorio GitHub creado.
- Tablero Trello creado.
- Discord habilitado.
- Plan de trabajo elaborado.
- Roles y alcance inicial definidos.
- Backlog del Sprint 1 preparado.

### En desarrollo

- Asignación de tareas.
- Contrato JSON.
- Diccionario de datos.
- Estrategia del dataset.
- Proyecto Spring Boot.
- Revisión de acceso a OCI.
- Wireframe.
- Preparación del EDA.

### Pendiente

- Dataset versión 1.
- Notebook con EDA.
- Modelo baseline.
- Integración modelo-API.
- Swagger.
- Manejo global de errores.
- Prueba de Object Storage.
- Dockerfile.
- Despliegue OCI.
- Video final.

---

## 17. Objetivo del Sprint 1

Construir el primer dataset utilizable, realizar el análisis exploratorio inicial y disponer de una API base que reciba, valide y responda al JSON del proyecto.

Resultados esperados:

- Dataset versión 1.
- Diccionario de datos.
- Notebook con EDA inicial.
- Reglas de clasificación.
- Modelo baseline.
- Proyecto Spring Boot.
- DTO y validaciones.
- Endpoint provisional.
- Swagger y manejo inicial de errores.
- Prueba de integración.
- Evidencia inicial de OCI.
- Wireframe del MVP.

---

## 18. Hitos

- **Semana 0:** integración, planificación y arquitectura.
- **Semana 1:** dataset, EDA, modelo baseline y API base.
- **Semana 2:** comparación de modelos e integración funcional.
- **Semana 3:** MVP completo y primer despliegue.
- **Semana 4:** Release Candidate, calidad y documentación.
- **Semana 5:** video, entregables y Demo Day.
- **Demo Day LATAM:** 25 o 27 de agosto de 2026.

---

## 19. Definición de terminado

Una tarea se considera terminada cuando:

- Cumple sus criterios de aceptación.
- Está disponible en el repositorio o carpeta acordada.
- Fue revisada y probada.
- Está integrada.
- Tiene documentación y evidencia.
- No contiene información sensible.

---

## 20. Riesgos

- Datos poco representativos.
- Desbalance de categorías.
- Dificultad de integración Python-Java.
- Acceso tardío a OCI.
- Crecimiento excesivo del alcance.
- Dependencia de una sola persona.
- Fallos durante la demostración.

Se mitigarán con pruebas tempranas, revisión cruzada, priorización del MVP y respaldos de la demo.

---

## 21. Enlaces

- **GitHub:** [No-Country-simulation/G9-LATAM-TEAM-09](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09)
- **Trello:** Hackathon ONE G9 - EnergiAI (tablero privado del equipo)
- **Discord:** disponible para el equipo.
- **Notebook:** pendiente.
- **Swagger:** pendiente.
- **API desplegada:** pendiente.
- **OCI:** pendiente.
- **Video demo:** pendiente.

> El enlace de Trello es una invitación. En la versión pública final deberá reemplazarse por un enlace de visualización o indicarse que el acceso es restringido.

---

## 22. Próximos pasos

1. Completar asignaciones en Trello.
2. Confirmar accesos a GitHub y OCI.
3. Definir contrato JSON y diccionario de datos.
4. Construir dataset versión 1.
5. Realizar EDA.
6. Entrenar modelo baseline.
7. Crear API Spring Boot.
8. Configurar Swagger y errores.
9. Probar integración modelo-API.
10. Preparar la Sprint Demo.
