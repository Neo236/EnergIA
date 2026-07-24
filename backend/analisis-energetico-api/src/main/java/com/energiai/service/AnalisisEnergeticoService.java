package com.energiai.service;

import org.springframework.stereotype.Service;

import com.energiai.dto.DatosRegistroAnalisis;
import com.energiai.dto.DatosRegistroConsumo;

@Service
public class AnalisisEnergeticoService {
    public DatosRegistroAnalisis realizarAnalisis(DatosRegistroConsumo datos){

        String categoria;
        Double probabilidad;
        String recomendaciones;

        // 1. Calculo de costo estimado provisional...
        double precio = datos.horarioPico() ? 120.0 : 100.0;
        double costoEstimado = datos.consumo() * precio;

        // 2. Logica de Clasificacion Prosivional
        if (datos.consumo() > 500 || datos.horasAltoConsumo() > 6){
            categoria = "INEFICIENTE";
            probabilidad = 0.90;
            recomendaciones = "Consumo elevado. Se recomienda apagar equipos de alto consumo durante el horario pico.";
        } else if (datos.consumo() > 200) {
            categoria = "MODERADO";
            probabilidad = 0.65;
            recomendaciones = "Consumo moderado. Optimizacion el uso de aire acondicionado y desconecta equipos en Stand-by.";
        } else {
            categoria = "EFICIENTE";
            probabilidad = 0.25;
            recomendaciones = "Excelente!!!! Tu nivel de consumo energetico es bajo y eficiente."; 
        }

        // 3. Retornamos el DTO de respuesta usando el @Builder
        return DatosRegistroAnalisis.builder()
        .categoria(categoria)
        .probabilidad(probabilidad)
        .costo_estimado_mensual(costoEstimado)
        .recomendaciones(recomendaciones)
        .build();
    }

}
