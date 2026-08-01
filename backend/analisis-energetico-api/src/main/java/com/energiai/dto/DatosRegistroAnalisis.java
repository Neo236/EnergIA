package com.energiai.dto;

import java.util.List;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Builder;

@Builder
public record DatosRegistroAnalisis( //response = salida

    @Schema(
        description = "Categoria del consumo (Eficiente, Moderado, Ineficiente)",
        example = "Ineficiente")
    CategoriaConsumo categoria,

    @Schema(
        description = "Nivel de probalidad de diagnostico (0.0 a 1.0)",
        example = "0.64")
    Double probabilidad,

    @Schema(
    description = "Lista de recomendaciones sugeridas por el sistema", 
    example = """
        [
          "Reducir el uso de equipos durante los horarios pico",
          "Evaluar equipos con alto consumo energético"
        ]
        """
    )
    List<String> recomendaciones,


    @Schema(
        description = "Costo mensual estimado en moneda local",
        example = "54060.0")
    Double costo_estimado_mensual
){

}
