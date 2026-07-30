package com.energiai.service;

import org.springframework.stereotype.Service;
import com.energiai.dto.DatosRegistroAnalisis;
import com.energiai.dto.DatosRegistroConsumo;
import java.util.List;

@Service
public class AnalisisEnergeticoService {
    public DatosRegistroAnalisis realizarAnalisis(DatosRegistroConsumo datos){

        String categoria;
        Double probabilidad;
        List<String> recomendaciones;

        // 1. Calculo de costo estimado provisional...
        double precio = datos.uso_horario_pico() ? 120.0 : 100.0;
        double costoEstimado = datos.consumo_kwh() * precio;

        // 2. Logica de Clasificacion Prosivional
        if (datos.consumo_kwh() > 500 || datos.horas_alto_consumo() > 6){
            categoria = "Ineficiente";
            probabilidad = 0.90;
            recomendaciones = List.of(
                "Consumo elevado detectado.",
                "Se recomienda apagar equipos de alto consumo durante el horario pico.",
                "Revisar facturas por posibles tarifas fuera de hora.",
                "Evaluar la eficiencia energética de los equipos actuales."
            );
        } else if (datos.consumo_kwh() > 200) {
            categoria = "Moderado";
            probabilidad = 0.65;
            recomendaciones = List.of(
                "Consumo moderado.",
                "Optimizar el uso de aire acondicionado.", //Posible cambio: Utilizar una variable para el nombre del equipo en lugar de hardcodear "aire acondicionado"
                "Desconectar equipos en modo Stand-by.",
                "Considerar iluminación LED."
            );
        } else {
            categoria = "Eficiente";
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
