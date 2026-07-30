package com.energiai.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.energiai.dto.DatosRegistroAnalisis;
import com.energiai.dto.DatosRegistroConsumo;
import com.energiai.service.AnalisisEnergeticoService;

import io.swagger.v3.oas.annotations.Operation;
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
        description = "Evalua los datos de consumo de un inmueble y devuelve la clasificacion provisional, costos estimados y recomendaciones."
    )

    @ApiResponses(value = {
        @ApiResponse(responseCode = "200",
        description = "Analisis realizado exitosamente."),
        @ApiResponse(responseCode = "400",
        description = "Datos de entradas invalidos o faltantes."),
        @ApiResponse(responseCode = "500",
        description = "Error interno al procesar el analisis.")
    })

    @PostMapping
    public ResponseEntity<DatosRegistroAnalisis> analizarConsumo(@Valid @RequestBody DatosRegistroConsumo request) {                                    
            DatosRegistroAnalisis resultado = analisisService.realizarAnalisis(request);
            return ResponseEntity.ok(resultado);
    }
}
