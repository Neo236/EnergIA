package com.energiai.dto;

import io.swagger.v3.oas.annotations.media.Schema;

@Schema(description = "Detalle de error en un campo especifico durante la validacion")
public record DatosErrorCampo(
    @Schema(description = "Nombre del campo con error", example = "consumo")
    String campo,

    @Schema(description = "Mensaje de error especifico del campo", example = "debe ser mayor que 0")
    String mensaje
) {}
