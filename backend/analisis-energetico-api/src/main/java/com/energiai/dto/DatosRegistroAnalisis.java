package com.energiai.dto;


import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Builder;

@Builder
public record DatosRegistroAnalisis( //response = salida

    @Schema(description = "Categoria del consumo (EFICIENTE, MODERADO, ALTO)", example = "ALTO")
    String categoria,

    @Schema(description = "Nivel de probalidad de diagnostico (0.0 a 1.0)", example = "0.64")
    Double probabilidad,

    @Schema(description = "Recomendacion sugerida por el sistema", example = "Se recomienda apagar equipos de alto consumo durante horario pico.")
    String recomendaciones,

    @Schema(description = "Costo mensual estimado en moneda local", example = "54060.0")
    Double costo_estimado_mensual
){

}
