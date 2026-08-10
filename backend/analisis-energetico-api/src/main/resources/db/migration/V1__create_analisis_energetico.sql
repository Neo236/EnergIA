-- Persistencia de los analisis de consumo energetico.
--
-- Tipos elegidos pensando en portar a Oracle mas adelante: NUMERIC (mapeado a
-- BigDecimal en la entidad) solo para el valor monetario, para evitar errores
-- de redondeo con dinero; DOUBLE PRECISION para las mediciones/probabilidad
-- (Double en la entidad, igual que ya se usa en el resto del contrato);
-- TIMESTAMP para fechas; VARCHAR para los enums (guardados como texto, no
-- como ordinal); y UUID (v7, generado en la app - ver UuidV7Generator) para
-- el id, en vez de un id secuencial: no es adivinable (hoy no hay
-- autenticacion) y no depende de una secuencia central de la base, lo que
-- ademas hace que migrar de motor no dependa de tener secuencias nativas.

CREATE TABLE analisis_energetico (
    id                      UUID PRIMARY KEY,
    fecha                   TIMESTAMP NOT NULL,

    -- Datos de entrada (espejo de DatosRegistroConsumo)
    consumo_kwh             DOUBLE PRECISION NOT NULL,
    cantidad_equipos        INTEGER NOT NULL,
    tipo_inmueble           VARCHAR(20) NOT NULL,
    uso_horario_pico        BOOLEAN,
    horas_alto_consumo      INTEGER NOT NULL,
    metros_cuadrados        INTEGER,
    antiguedad_vivienda     INTEGER,
    zona_fria               BOOLEAN,
    calidad_aislamiento     VARCHAR(20),
    fuente_calefaccion      VARCHAR(20),
    fuente_agua_caliente    VARCHAR(20),

    -- Resultado del analisis (espejo de DatosRegistroAnalisis)
    categoria               VARCHAR(20) NOT NULL,
    probabilidad            DOUBLE PRECISION NOT NULL,
    costo_estimado_mensual  NUMERIC(10,2) NOT NULL
);

CREATE TABLE analisis_energetico_recomendaciones (
    analisis_id     UUID NOT NULL REFERENCES analisis_energetico(id),
    orden           INTEGER NOT NULL,
    recomendacion   VARCHAR(255) NOT NULL,
    PRIMARY KEY (analisis_id, orden)
);
