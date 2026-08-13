package com.energiai.service;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.UUID;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.energiai.client.MlClient;
import com.energiai.dto.DatosRegistroAnalisis;
import com.energiai.dto.DatosRegistroConsumo;
import com.energiai.entity.AnalisisEnergeticoEntity;
import com.energiai.exception.MlRespuestaInvalidaException;
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

    // esSonda: true cuando la peticion trae la cabecera secreta X-EnergiAI-Sonda
    // valida (verificada en el controller). Identifica una verificacion
    // automatica de CI/CD (ver docs/cicd/README.md), no un analisis real: se
    // sigue llamando al ML de verdad -es la unica forma de validar el circuito
    // completo- pero el resultado no se persiste ni queda con id/fecha, para
    // no ensuciar la base con datos sinteticos.
    public DatosRegistroAnalisis realizarAnalisis(DatosRegistroConsumo datos, boolean esSonda) {
        if (mlClient == null) {
            throw new ServicioMlNoDisponibleException("El servicio Machine Learning no se encuentra disponible");
        }
        // La llamada al servicio ML queda fuera de la transaccion de guardado
        // (repository.save la abre y la cierra sola): no tiene sentido mantener
        // una conexion de base de datos abierta mientras se espera la red.
        DatosRegistroAnalisis resultadoMl = mlClient.predecir(datos);
        validarRespuestaMl(resultadoMl);

        if (esSonda) {
            return resultadoMl;
        }

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
    public DatosRegistroAnalisis obtenerAnalisisPorId(UUID id) {
        AnalisisEnergeticoEntity entidad = repository.findById(id)
                .orElseThrow(() -> new RecursoNoEncontradoException("Analisis no encontrado con ID " + id));
        return paraDto(entidad);
    }

    // MlClient solo valida que la respuesta sea JSON deserializable, no que
    // traiga los campos obligatorios completos. Un JSON valido pero con
    // "costo_estimado_mensual": null pasaria sin error hasta aca y despues
    // tiraria NullPointerException al desempaquetar el Double (o violaria
    // el NOT NULL de la columna al guardar) - en ambos casos, un 500
    // generico que parece un bug propio en vez de un problema del ML. Se
    // valida tambien para las peticiones sonda: son la unica prueba que
    // recorre API -> ml-service -> modelo de punta a punta, y perderia el
    // sentido si no detectara una respuesta incompleta.
    private void validarRespuestaMl(DatosRegistroAnalisis resultadoMl) {
        if (resultadoMl.categoria() == null || resultadoMl.probabilidad() == null
                || resultadoMl.costo_estimado_mensual() == null) {
            throw new MlRespuestaInvalidaException(
                    "El servicio Machine Learning no devolvió los campos obligatorios del análisis");
        }
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
