package com.energiai.service;

import java.math.BigDecimal;
import java.time.LocalDateTime;

import org.springframework.stereotype.Service;

import com.energiai.client.MlClient;
import com.energiai.dto.DatosRegistroAnalisis;
import com.energiai.dto.DatosRegistroConsumo;
import com.energiai.entity.AnalisisEnergeticoEntity;
import com.energiai.exception.RecursoNoEncontradoException;
import com.energiai.exception.ServicioMlNoDisponibleException;
import com.energiai.repository.AnalisisEnergeticoRepository;

@Service
public class AnalisisEnergeticoService {

    private final MlClient mlClient;
    private final AnalisisEnergeticoRepository repository;

    public AnalisisEnergeticoService(MlClient mlClient, AnalisisEnergeticoRepository repository) {
        this.mlClient = mlClient;
        this.repository = repository;
    }

    public DatosRegistroAnalisis realizarAnalisis(DatosRegistroConsumo datos) {
        if (mlClient == null) {
            throw new ServicioMlNoDisponibleException("El servicio Machine Learning no se encuentra disponible");
        }
        // La llamada al servicio ML queda fuera de la transaccion de guardado
        // (repository.save la abre y la cierra sola): no tiene sentido mantener
        // una conexion de base de datos abierta mientras se espera la red.
        DatosRegistroAnalisis resultadoMl = mlClient.predecir(datos);
        AnalisisEnergeticoEntity guardado = repository.save(paraEntidad(datos, resultadoMl));
        return paraDto(guardado);
    }

    public DatosRegistroAnalisis obtenerAnalisisPorId(Long id) {
        AnalisisEnergeticoEntity entidad = repository.findById(id)
                .orElseThrow(() -> new RecursoNoEncontradoException("Analisis no encontrado con ID " + id));
        return paraDto(entidad);
    }

    private AnalisisEnergeticoEntity paraEntidad(DatosRegistroConsumo datos, DatosRegistroAnalisis resultadoMl) {
        return new AnalisisEnergeticoEntity(
                LocalDateTime.now(),
                datos.consumo_kwh(),
                datos.cantidad_equipos(),
                datos.tipo_inmueble(),
                datos.uso_horario_pico(),
                datos.horas_alto_consumo(),
                datos.metros_cuadrados(),
                datos.antiguedad_vivienda(),
                datos.zona_fria(),
                datos.calidad_aislamiento(),
                datos.fuente_calefaccion(),
                datos.fuente_agua_caliente(),
                resultadoMl.categoria(),
                resultadoMl.probabilidad(),
                BigDecimal.valueOf(resultadoMl.costo_estimado_mensual()),
                resultadoMl.recomendaciones()
        );
    }

    private DatosRegistroAnalisis paraDto(AnalisisEnergeticoEntity entidad) {
        return DatosRegistroAnalisis.builder()
                .id(entidad.getId())
                .fecha(entidad.getFecha())
                .categoria(entidad.getCategoria())
                .probabilidad(entidad.getProbabilidad())
                .costo_estimado_mensual(entidad.getCostoEstimadoMensual().doubleValue())
                .recomendaciones(entidad.getRecomendaciones())
                .build();
    }
}
