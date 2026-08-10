package com.energiai.dto;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Builder;

@Builder
public record DatosRegistroAnalisis( //response = salida

    @Schema(
        description = "Identificador unico del analisis (UUID v7), asignado al persistirlo",
        example = "018f4e2a-7c3b-7b9e-8b1a-2f6c9d3e5a10")
    UUID id,

    @Schema(
        description = "Fecha y hora en que se realizo el analisis",
        example = "2026-08-10T11:45:00")
    LocalDateTime fecha,

    @Schema(
        description = "Categoria del consumo (Eficiente, Moderado, Ineficiente)",
        example = "Ineficiente")
    CategoriaConsumo categoria,

    @Schema(
        description = "Nivel de probalidad de diagnostico (0.0 a 1.0)",
        example = "0.64",
        minimum = "0.0",
        maximum = "1.0"
    )
    Double probabilidad,
    @Schema(
        description = "Costo mensual estimado en moneda local",
        example = "377.88")
    Double costo_estimado_mensual,

    @Schema(
    description = "Lista de recomendaciones sugeridas por el sistema",
    example = """
        [
          "Reducir el uso de equipos durante los horarios pico",
          "Evaluar equipos con alto consumo energético"
        ]
        """
    )
    List<String> recomendaciones
){

}
