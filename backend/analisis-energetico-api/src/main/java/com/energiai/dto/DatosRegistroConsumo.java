package com.energiai.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;


public record DatosRegistroConsumo ( //Request => Entrada

    @Schema(
        description = "Consumo electrico total en KWh",
        example = "450.5")
    @NotNull @Positive 
    Double consumo_kwh,

    @Schema(
        description = "Cantidad de equipos activos",
        example = "8")
    @NotNull @Min(value = 1) @Max(value = 100)
    Integer cantidad_equipos,

    @Schema(
        description = "Tipo de inmueble (Casa, Departamento, Comercio, Pyme)",
        example = "Casa")
    @NotNull
    TipoInmueble tipo_inmueble,

    @Schema(
        description = "Indica si la medicion incluye franja de horario pico (18hs a 23hs) - Igual a 0 es false y distinto a 0 es true.",
        example = "true")
    @NotNull
    Boolean uso_horario_pico,

    @Schema(
        description = "Horas estimadas de uso de equipos de alto consumo al dia.",
        example = "6")
    @NotNull @Min(value = 0) @Max(value = 24)
    Integer horas_alto_consumo,

    @Schema(
        description = "Superficie total habitale de la vivienda, expresada en metros cuadrados.",
        example = "30")
    @NotNull @Min(value = 26) @Max(value = 2000)
    Integer metros_cuadrados,

    @Schema(
        description = "Cantidad de años transcurridos desde la construccion.",
        example = "34")
    @NotNull @Min(value = 0) @Max(value = 150)
    Integer antiguedad_vivienda,

    @Schema(
        description = "Indica si la vivienda se encuentra ubicada en una zona climatica considerada fria.",
        example = "No")
    @NotNull
    Boolean zona_fria,

    @Schema(
        description = "Nivel de eficiencia del aislamiento térmico.",
        example = "MEDIA")
    @NotNull
    CalidadAislamiento calidad_aislamiento,

    @Schema(
        description = "Fuente principal de energia utilizada para la calefaccion.",
        example = "SOLAR")
    @NotNull
    FuenteEnergia fuente_calefaccion,

    @Schema(
        description = "Fuente de energia uitlizada para la produccion de agua caliente sanitaria.",
        example = "ELECTRICIDAD")
    @NotNull
    FuenteEnergia fuente_agua_caliente

) {

}