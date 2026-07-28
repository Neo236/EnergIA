package com.energiai.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
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
        description = "Tipo de inmuebles (RESIDENCIAL, COMERCIAL, INDUSTRIAL)",
        example = "RESIDENCIAL")
    @NotBlank 
    @Pattern(
        regexp = "^(Casa|Departamento|Comercio|Pyme)$",
        message = "El tipo de inmueble debe ser: Casa, Departamento, Comercio o Pyme")
    String tipo_inmueble,

    @Schema(
        description = "Indica si la medicion incluye franja de horario pico (18hs a 23hs)",
        example = "true")
    @NotNull
    Boolean uso_horario_pico,

    @Schema(
        description = "Horas estimadas de uso de equipos de alto consumo al dia",
        example = "6")
    @NotNull @Min(value = 0) @Max(value = 24)
    Integer horas_alto_consumo
) {

}