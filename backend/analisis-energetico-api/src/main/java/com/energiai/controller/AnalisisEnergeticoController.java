package com.energiai.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.energiai.dto.DatosErrorRespuesta;
import com.energiai.dto.DatosRegistroAnalisis;
import com.energiai.dto.DatosRegistroConsumo;
import com.energiai.service.AnalisisEnergeticoService;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.ExampleObject;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;

@RestController
@RequestMapping("/api/v1/analisis-energetico")
@Tag(name = "Analisis Energetico",
description = "Endpoints para el diagnostico y evaluacion de consumo electronico")
public class AnalisisEnergeticoController {

    @Autowired
    private AnalisisEnergeticoService analisisService;

    @Operation(
        summary = "Realizar analisis de consumo energetico",
        description = "Evalua los datos de consumo de un inmueble y devuelve la clasificacion, costos estimados y recomendaciones."
    )

    @ApiResponses(value = {
            @ApiResponse(
                responseCode = "200",
                description = "Análisis realizado exitosamente.",
                content = @Content(
                    mediaType = "application/json",
                    schema = @Schema(implementation = DatosRegistroAnalisis.class),
                    examples = @ExampleObject(
                        value = """
                        {
                            "id": 1,
                            "fecha": "2026-08-10T11:45:00",
                            "categoria": "Eficiente",
                            "probabilidad": 0.25,
                            "costo_estimado_mensual": 337.87,
                            "recomendaciones": [
                                "Excelente nivel de consumo.",
                                "Mantener los hábitos actuales de ahorro.",
                                "Continuar monitoreando el consumo mensual."
                            ]
                        }
                            """
                    )
                )
            ),
            @ApiResponse(
                responseCode = "400",
                description = "Datos de entrada inválidos o formato JSON incorrecto.",
                content = @Content(
                    mediaType = "application/json",
                    schema = @Schema(implementation = DatosErrorRespuesta.class),
                    examples = @ExampleObject(
                        value = """
                        {
                          "timestamp": "2026-08-01T16:45:00",
                          "status": 400,
                          "error": "BAD_REQUEST",
                          "mensaje": "Errores de validacion en los datos de entrada",
                          "detalles": [
                            {
                              "campo": "cantidad_equipos",
                              "mensaje": "no debe ser nulo"
                            },
                            {
                              "campo": "horas_alto_consumo",
                              "mensaje": "no debe ser nulo"
                            }
                          ]
                        }
                        """
                    )
                )
            ),
            @ApiResponse(
                responseCode = "404",
                description = "El recurso solicitado o la ruta no fueron encontrados.",
                content = @Content(
                    mediaType = "application/json",
                    schema = @Schema(implementation = DatosErrorRespuesta.class),
                    examples = @ExampleObject(
                        value = """
                        {
                          "timestamp": "2026-08-01T16:45:00",
                          "status": 404,
                          "error": "NOT_FOUND",
                          "mensaje": "El recurso solicitado no fue encontrado"
                        }
                        """
                    )
                )
            ),
            @ApiResponse(
                responseCode = "500",
                description = "Error interno del servidor.",
                content = @Content(
                    mediaType = "application/json",
                    schema = @Schema(implementation = DatosErrorRespuesta.class),
                    examples = @ExampleObject(
                        value = """
                        {
                          "timestamp": "2026-08-01T16:45:00",
                          "status": 500,
                          "error": "INTERNAL_SERVER_ERROR",
                          "mensaje": "Ocurrio un error interno en el servidor. Por favor, intente mas tarde."
                        }
                        """
                    )
                )
            ),
            @ApiResponse(
                responseCode = "503",
                description = "El servicio de Machine Learning no se encuentra disponible.",
                content = @Content(
                    mediaType = "application/json",
                    schema = @Schema(implementation = DatosErrorRespuesta.class),
                    examples = @ExampleObject(
                        value = """
                        {
                          "timestamp": "2026-08-01T16:45:00",
                          "status": 503,
                          "error": "SERVICE_UNAVAILABLE",
                          "mensaje": "El servicio de Machine Learning no se encuentra disponible."
                        }
                        """
                    )
                )
            ),
            @ApiResponse(
                responseCode = "502",
                description = "El servicio de Machine Learning devolvió una respuesta inesperada o inválida.",
                content = @Content(
                    mediaType = "application/json",
                    schema = @Schema(implementation = DatosErrorRespuesta.class),
                    examples = @ExampleObject(
                        value = """
                        {
                          "timestamp": "2026-08-01T16:45:00",
                          "status": 502,
                          "error": "BAD_GATEWAY",
                          "mensaje": "El servicio de Machine Learning devolvió una respuesta inesperada o inválida"
                        }
                        """
                    )
                )
            )
        })

    @PostMapping
    public ResponseEntity<DatosRegistroAnalisis> analizarConsumo(@Valid @RequestBody DatosRegistroConsumo request) {
            DatosRegistroAnalisis resultado = analisisService.realizarAnalisis(request);
            return ResponseEntity.ok(resultado);
    }

    @Operation(
        summary = "Consultar un analisis previamente realizado",
        description = "Devuelve un analisis de consumo energetico ya guardado, a partir de su identificador."
    )
    @ApiResponses(value = {
            @ApiResponse(
                responseCode = "200",
                description = "Analisis encontrado.",
                content = @Content(
                    mediaType = "application/json",
                    schema = @Schema(implementation = DatosRegistroAnalisis.class),
                    examples = @ExampleObject(
                        value = """
                        {
                            "id": 1,
                            "fecha": "2026-08-10T11:45:00",
                            "categoria": "Eficiente",
                            "probabilidad": 0.25,
                            "costo_estimado_mensual": 337.87,
                            "recomendaciones": [
                                "Excelente nivel de consumo.",
                                "Mantener los hábitos actuales de ahorro.",
                                "Continuar monitoreando el consumo mensual."
                            ]
                        }
                        """
                    )
                )
            ),
            @ApiResponse(
                responseCode = "404",
                description = "No existe un analisis con el id indicado.",
                content = @Content(
                    mediaType = "application/json",
                    schema = @Schema(implementation = DatosErrorRespuesta.class),
                    examples = @ExampleObject(
                        value = """
                        {
                          "timestamp": "2026-08-10T11:45:00",
                          "status": 404,
                          "error": "NOT_FOUND",
                          "mensaje": "Analisis no encontrado con ID 999"
                        }
                        """
                    )
                )
            )
        })
    @GetMapping("/{id}")
    public ResponseEntity<DatosRegistroAnalisis> obtenerAnalisis(
            @Parameter(description = "Identificador del analisis", example = "1") @PathVariable Long id) {
        DatosRegistroAnalisis resultado = analisisService.obtenerAnalisisPorId(id);
        return ResponseEntity.ok(resultado);
    }
}
