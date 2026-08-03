package com.energiai.service;

import java.util.List;

import org.springframework.stereotype.Service;

import com.energiai.dto.CategoriaConsumo;
import com.energiai.dto.DatosRegistroAnalisis;
import com.energiai.dto.DatosRegistroConsumo;


@Service
public class AnalisisEnergeticoService {
    public DatosRegistroAnalisis realizarAnalisis(DatosRegistroConsumo datos){

        // if(true){
        //     throw new ServicioMlNoDisponibleException("El servicio Machine Learning no se encuentra disponible");
        // }

        CategoriaConsumo categoria;
        Double probabilidad;
        List<String> recomendaciones;

        // 1. Calculo de costo estimado con tarifa acordada de $0.75/kWh
        double precio = 0.75;
        double costoEstimado = Math.round((datos.consumo_kwh() * precio) * 100.0) / 100.0;

        // 2. Logica de Clasificacion Prosivional
        if (datos.consumo_kwh() > 500 || datos.horas_alto_consumo() > 6){
            categoria = CategoriaConsumo.INEFICIENTE;
            probabilidad = 0.90;
            recomendaciones = List.of(
                "Consumo elevado detectado.",
                "Se recomienda apagar equipos de alto consumo durante el horario pico.",
                "Revisar facturas por posibles tarifas fuera de hora.",
                "Evaluar la eficiencia energética de los equipos actuales."
            );
        } else if (datos.consumo_kwh() > 200) {
            categoria = CategoriaConsumo.MODERADO;
            probabilidad = 0.65;
            recomendaciones = List.of(
                "Consumo moderado.",
                "Optimizar el uso de aire acondicionado.",
                "Desconectar equipos en modo Stand-by.",
                "Considerar iluminación LED."
            );
        } else {
            categoria = CategoriaConsumo.EFICIENTE;
            probabilidad = 0.25;
            recomendaciones = List.of(
                "Excelente nivel de consumo.",
                "Mantener los hábitos actuales de ahorro.",
                "Continuar monitoreando el consumo mensual."
            );
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

