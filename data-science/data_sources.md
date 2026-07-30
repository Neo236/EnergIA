# Estrategia y Fuentes de Datos

**Proyecto:** EnergIA – Hackathon ONE G9 
**Repositorio:** `data-science/`  
**Documento:** Estrategia y Fuentes de Datos  
**Versión:** 1.0  
**Última actualización:** 26 Julio 2026

---

# 1. Objetivo

Este documento define la estrategia utilizada para construir el dataset del proyecto **EnergIA**, cuyo propósito es desarrollar un modelo capaz de analizar patrones de consumo eléctrico residencial y clasificar el perfil energético de una vivienda.

En este documento se describen:

- Las fuentes públicas revisadas.
- Las variables disponibles en dichas fuentes.
- Las variables que deben ser simuladas.
- La estrategia de construcción del dataset.
- Los criterios de reproducibilidad.
- Los supuestos utilizados.
- Las limitaciones identificadas.
- Los riesgos asociados a la generación del dataset.

Este documento da cumplimiento a los criterios de aceptación definidos para la actividad **"Definir cómo se construirá la base de datos del proyecto"**.

---

# 2. Estrategia de construcción del dataset

El proyecto utilizará un **dataset híbrido**, combinando información proveniente de fuentes públicas con datos generados mediante simulación.

Esta estrategia fue seleccionada debido a que actualmente no existe un conjunto de datos público que contenga todas las variables necesarias para caracterizar el consumo energético residencial y entrenar un modelo de clasificación acorde a los objetivos del proyecto.

Las fuentes públicas se utilizarán únicamente como referencia estadística para definir rangos, distribuciones y valores plausibles.

Los registros finales del dataset serán generados mediante simulación, permitiendo contar con una base de datos consistente, reproducible y adaptada a las necesidades del proyecto.

---

# 3. Criterios de selección de las fuentes

Las fuentes públicas fueron seleccionadas considerando los siguientes criterios:

- Información proveniente de organismos oficiales e internacionales.
- Acceso público y gratuito.
- Cobertura para países de América Latina.
- Datos actualizados periódicamente.
- Calidad y confiabilidad reconocidas internacionalmente.
- Compatibilidad con las variables requeridas por el proyecto.

Con base en estos criterios se seleccionaron el **World Bank Open Data** y la **International Energy Agency (IEA)** como fuentes oficiales de referencia.

---

# 4. Fuentes públicas utilizadas

## 4.1 World Bank Open Data

**Organización**

World Bank

**Portal oficial**

https://data.worldbank.org/

El Banco Mundial proporciona indicadores demográficos y socioeconómicos que permiten construir perfiles de hogares representativos para América Latina.

### Indicadores utilizados

| Indicador | Código | Uso en el proyecto |
|-----------|---------|-------------------|
| Access to electricity (% of population) | EG.ELC.ACCS.ZS | Validar el acceso al suministro eléctrico de los hogares |
| Urban population (% of total population) | SP.URB.TOTL.IN.ZS | Definir la distribución de hogares urbanos |
| GDP per capita (current US$) | NY.GDP.PCAP.CD | Referencia para la simulación del nivel socioeconómico |

### Referencias oficiales

- https://data.worldbank.org/indicator/EG.ELC.ACCS.ZS
- https://data.worldbank.org/indicator/SP.URB.TOTL.IN.ZS
- https://data.worldbank.org/indicator/NY.GDP.PCAP.CD

---

## 4.2 International Energy Agency (IEA)

**Organización**

International Energy Agency (IEA)

**Portal oficial**

https://www.iea.org/data-and-statistics

La Agencia Internacional de Energía proporciona estadísticas oficiales relacionadas con el consumo energético residencial y la eficiencia energética.

### Fuente utilizada

**Energy End-uses and Efficiency Indicators Data Explorer**

https://www.iea.org/data-and-statistics/data-tools/energy-efficiency-indicators-data-explorer

### Información utilizada

- Consumo eléctrico residencial.
- Consumo final de electricidad por sector.
- Indicadores de eficiencia energética.
- Demanda energética residencial.

---

# 5. Tipo de dataset

El dataset estará compuesto por información pública de referencia y datos sintéticos generados mediante simulación.

| Componente | Tipo |
|------------|------|
| Estadísticas de referencia | Público |
| Información de hogares | Sintético |
| Equipamiento del hogar | Sintético |
| Consumo energético | Sintético |
| Costo mensual de energía | Calculado |
| Clasificación energética | Calculada mediante reglas |

**Clasificación del dataset:** Híbrido.

---

# 6. Variables disponibles en fuentes públicas

Las siguientes variables cuentan con respaldo en información pública y serán utilizadas como referencia para la generación del dataset.

| Variable | Fuente | Uso |
|----------|--------|-----|
| Acceso a electricidad | World Bank | Validar disponibilidad del servicio eléctrico |
| Población urbana | World Bank | Definir distribución de hogares |
| PIB per cápita | World Bank | Referencia socioeconómica |
| Consumo eléctrico residencial | IEA | Definir rangos de consumo |
| Indicadores de eficiencia energética | IEA | Apoyar las reglas de clasificación |

Estas variables **no serán copiadas directamente** al dataset, sino que servirán como referencia estadística para la simulación.

---

# 7. Variables simuladas

Las siguientes variables serán generadas mediante reglas estadísticas y algoritmos de simulación.

| Variable | Método de generación |
|----------|----------------------|
| Tamaño del hogar | Distribución estadística |
| Tipo de vivienda | Selección probabilística |
| Consumo mensual (kWh) | Simulación basada en rangos IEA |
| Cantidad de electrodomésticos | Reglas de simulación |
| Antigüedad de los electrodomésticos | Distribución estadística |
| Patrón de ocupación | Distribución probabilística |
| Horario de mayor consumo | Distribución probabilística |
| Uso de energías renovables | Asignación aleatoria |
| Costo mensual (USD) | Cálculo automático |
| Clasificación energética | Reglas de clasificación |

---

# 8. Trazabilidad de las variables

La siguiente tabla resume el origen de las principales variables del proyecto.

| Variable | Fuente pública | Simulada | Calculada |
|----------|----------------|:--------:|:---------:|
| Acceso a electricidad | World Bank | ❌ | ❌ |
| Consumo residencial (referencia) | IEA | ❌ | ❌ |
| Tamaño del hogar | — | ✅ | ❌ |
| Cantidad de electrodomésticos | — | ✅ | ❌ |
| Horario de mayor consumo | — | ✅ | ❌ |
| Consumo mensual del hogar | IEA (rangos) | ✅ | ❌ |
| Costo mensual | — | ❌ | ✅ |
| Clasificación energética | — | ❌ | ✅ |

---

# 9. Flujo de construcción del dataset

```text
              World Bank
                    │
                    │
                    ▼
        Parámetros demográficos
                    │
                    │
IEA ─────► Parámetros energéticos
                    │
                    ▼
      Generador de datos sintéticos
                    │
                    ▼
     Dataset (2.000 hogares)
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
         EDA        Entrenamiento del modelo
```

---

# 10. Proceso de generación del dataset

La construcción del dataset sigue las siguientes etapas:

1. Revisión de fuentes públicas.
2. Definición de parámetros estadísticos.
3. Inicialización de la semilla aleatoria.
4. Generación de información de los hogares.
5. Simulación del equipamiento eléctrico.
6. Simulación del consumo energético mensual.
7. Cálculo del costo mensual.
8. Aplicación de reglas de clasificación.
9. Exportación del dataset en formato CSV.

---

# 11. Reproducibilidad

Con el objetivo de garantizar la reproducibilidad del proyecto, la generación del dataset utiliza una semilla aleatoria fija.

```python
RANDOM_SEED = 42

import random
import numpy as np

random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)
```

La utilización de la misma semilla permite obtener exactamente el mismo conjunto de datos al ejecutar nuevamente el proceso de generación.

---

# 12. Tamaño inicial del dataset

La primera versión del proyecto considera un dataset compuesto por **2.000 hogares sintéticos**.

Este tamaño fue definido porque proporciona una cantidad suficiente de observaciones para:

- Realizar análisis exploratorio de datos (EDA).
- Construir variables derivadas.
- Entrenar modelos de Machine Learning.
- Validar los resultados obtenidos.
- Mantener tiempos de procesamiento reducidos durante el desarrollo.

El tamaño del dataset podrá incrementarse en futuras versiones del proyecto.

---

# 13. Supuestos

Para la construcción del dataset se consideran los siguientes supuestos:

- El dataset representa hogares residenciales de América Latina.
- Cada registro corresponde a un único hogar.
- No se utilizan datos personales reales.
- Las fuentes públicas se emplean únicamente como referencia estadística.
- Las variables inexistentes en fuentes públicas son simuladas mediante reglas estadísticas.
- El consumo eléctrico residencial se genera utilizando rangos basados en información publicada por la IEA.
- La distribución socioeconómica toma como referencia indicadores publicados por el World Bank.
- Se utiliza una tarifa de referencia de **USD 0,75 por kWh**, conforme a las recomendaciones del Hackathon.

---

# 14. Limitaciones

La primera versión del dataset presenta las siguientes limitaciones:

- No representa un país específico.
- Varias variables son sintéticas debido a la inexistencia de un dataset público completo.
- No incorpora variaciones estacionales del consumo.
- No considera diferencias tarifarias entre países.
- No modela eventos extraordinarios como cortes de suministro o fenómenos climáticos.

---

# 15. Riesgos identificados

| Riesgo | Impacto | Mitigación |
|---------|---------|------------|
| Ausencia de variables públicas | Medio | Generación mediante simulación |
| Distribuciones poco realistas | Medio | Validación con estadísticas oficiales |
| Sobreajuste del modelo | Medio | Validación cruzada |
| Inconsistencias en el dataset | Bajo | Reglas de validación durante la generación |
| Cambios en las estadísticas oficiales | Bajo | Actualización y versionado de las fuentes |

---

# 16. Referencias

1. World Bank. **World Development Indicators**. https://data.worldbank.org/

2. World Bank. **Access to electricity (% of population)**.  
https://data.worldbank.org/indicator/EG.ELC.ACCS.ZS

3. World Bank. **Urban population (% of total population)**.  
https://data.worldbank.org/indicator/SP.URB.TOTL.IN.ZS

4. World Bank. **GDP per capita (current US$)**.  
https://data.worldbank.org/indicator/NY.GDP.PCAP.CD

5. International Energy Agency (IEA). **Data & Statistics**.  
https://www.iea.org/data-and-statistics

6. International Energy Agency (IEA). **Energy End-uses and Efficiency Indicators Data Explorer**.  
https://www.iea.org/data-and-statistics/data-tools/energy-efficiency-indicators-data-explorer

7. Hackathon ONE G9 – Alura + Oracle. Documento técnico del desafío.

---

**Elaborado por:** Equipo de Ciencia de Datos – EnergIA  
