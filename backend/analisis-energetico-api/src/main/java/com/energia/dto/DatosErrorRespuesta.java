package com.energia.dto;

import java.time.LocalDateTime;
import java.util.List;

import com.fasterxml.jackson.annotation.JsonInclude;

import io.swagger.v3.oas.annotations.media.Schema;

@Schema(
    description = "Respuesta de error uniforme de la API")
@JsonInclude(JsonInclude.Include.NON_NULL)
public record DatosErrorRespuesta(
    @Schema(
        description = "Fecha y hora en que ocurrio el error", example = "2026-07-23T11:45:00")
    LocalDateTime timestamp,

    @Schema(
        description = "Codigo de estado HTTP numerico", example = "400")
    Integer status,

    @Schema(
        description = "Tipo o nombre corto del error HTTP", example = "BAD_REQUEST")
    String error,

    @Schema(
        description = "Mensaje general explicativo del error", example = "Los datos ingresados son invalidos")
    String mensaje,

    @Schema(
        description = "Lista detallada de errores por campo (solo si aplica)")
    List<DatosErrorCampo> detalles
) {
    public static DatosErrorRespuesta de(Integer status, String error, String mensaje) {
        return new DatosErrorRespuesta(LocalDateTime.now(), status, error, mensaje, null);
    }

    public static DatosErrorRespuesta de(Integer status, String error, String mensaje, List<DatosErrorCampo> detalles) {
        return new DatosErrorRespuesta(LocalDateTime.now(), status, error, mensaje, detalles);
    }
}
