package com.energiai.service;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

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

    // readOnly=true: sin esto, la coleccion "recomendaciones" (LAZY) solo se
    // podia leer en paraDto() gracias a Open Session In View (activado por
    // defecto en Spring Boot) manteniendo la sesion de Hibernate abierta
    // durante toda la request. Con la transaccion explicita, la lectura deja
    // de depender de ese comportamiento implicito (que ademas mantiene la
    // conexion a la DB ocupada mas tiempo del necesario) y open-in-view se
    // puede desactivar sin romper nada.
    @Transactional(readOnly = true)
    public DatosRegistroAnalisis obtenerAnalisisPorId(Long id) {
        AnalisisEnergeticoEntity entidad = repository.findById(id)
                .orElseThrow(() -> new RecursoNoEncontradoException("Analisis no encontrado con ID " + id));
        return paraDto(entidad);
    }

    private AnalisisEnergeticoEntity paraEntidad(DatosRegistroConsumo datos, DatosRegistroAnalisis resultadoMl) {
        return AnalisisEnergeticoEntity.builder()
                .fecha(LocalDateTime.now())
                .consumoKwh(datos.consumo_kwh())
                .cantidadEquipos(datos.cantidad_equipos())
                .tipoInmueble(datos.tipo_inmueble())
                .usoHorarioPico(datos.uso_horario_pico())
                .horasAltoConsumo(datos.horas_alto_consumo())
                .metrosCuadrados(datos.metros_cuadrados())
                .antiguedadVivienda(datos.antiguedad_vivienda())
                .zonaFria(datos.zona_fria())
                .calidadAislamiento(datos.calidad_aislamiento())
                .fuenteCalefaccion(datos.fuente_calefaccion())
                .fuenteAguaCaliente(datos.fuente_agua_caliente())
                .categoria(resultadoMl.categoria())
                .probabilidad(resultadoMl.probabilidad())
                .costoEstimadoMensual(BigDecimal.valueOf(resultadoMl.costo_estimado_mensual()))
                .recomendaciones(resultadoMl.recomendaciones())
                .build();
    }

    private DatosRegistroAnalisis paraDto(AnalisisEnergeticoEntity entidad) {
        return DatosRegistroAnalisis.builder()
                .id(entidad.getId())
                .fecha(entidad.getFecha())
                .categoria(entidad.getCategoria())
                .probabilidad(entidad.getProbabilidad())
                .costo_estimado_mensual(entidad.getCostoEstimadoMensual().doubleValue())
                // Copia a un ArrayList plano DENTRO de la transaccion: solo pasar la
                // referencia (entidad.getRecomendaciones()) no alcanza, porque un
                // getter no dispara la carga de una coleccion @ElementCollection
                // LAZY por si solo. Sin esto, el fetch real ocurre recien al
                // serializar la respuesta, ya con la sesion de Hibernate cerrada
                // (LazyInitializationException), aunque el metodo sea @Transactional.
                .recomendaciones(new ArrayList<>(entidad.getRecomendaciones()))
                .build();
    }
}
