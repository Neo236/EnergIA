package com.energiai.entity;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

import com.energiai.dto.CalidadAislamiento;
import com.energiai.dto.CategoriaConsumo;
import com.energiai.dto.FuenteEnergia;
import com.energiai.dto.TipoInmueble;

import jakarta.persistence.CollectionTable;
import jakarta.persistence.Column;
import jakarta.persistence.ElementCollection;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.OrderColumn;
import jakarta.persistence.Table;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.UuidGenerator;

// Persiste tanto los datos de entrada como el resultado de cada analisis.
// Los enums se guardan como texto (EnumType.STRING) para que la tabla no
// dependa del orden de declaracion en el codigo.
//
// El constructor es privado y solo se llega a el via el builder (Lombok):
// con 15 campos, varios del mismo tipo (Boolean, Integer), un constructor
// posicional es un riesgo real de mezclar valores en el orden equivocado
// sin que el compilador lo note.
@Entity
@Table(name = "analisis_energetico")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED) // Requerido por JPA.
public class AnalisisEnergeticoEntity {

    // UUID v7, no un id secuencial: no es adivinable (hoy no hay
    // autenticacion, asi que un id numerico dejaria cualquier analisis
    // accesible con solo probar /1, /2, /3...) y se genera en la app sin
    // depender de una secuencia central de la base. Generador nativo de
    // Hibernate (RFC 9562): timestamp de milisegundos en los primeros 48
    // bits + el resto aleatorio, lo que mantiene el orden de insercion en el
    // indice sin necesitar coordinacion externa.
    @Id
    @UuidGenerator(style = UuidGenerator.Style.VERSION_7)
    private UUID id;

    @Column(name = "fecha", nullable = false)
    private LocalDateTime fecha;

    @Column(name = "consumo_kwh", nullable = false)
    private Double consumoKwh;

    @Column(name = "cantidad_equipos", nullable = false)
    private Integer cantidadEquipos;

    @Enumerated(EnumType.STRING)
    @Column(name = "tipo_inmueble", nullable = false, length = 20)
    private TipoInmueble tipoInmueble;

    @Column(name = "uso_horario_pico")
    private Boolean usoHorarioPico;

    @Column(name = "horas_alto_consumo", nullable = false)
    private Integer horasAltoConsumo;

    @Column(name = "metros_cuadrados")
    private Integer metrosCuadrados;

    @Column(name = "antiguedad_vivienda")
    private Integer antiguedadVivienda;

    @Column(name = "zona_fria")
    private Boolean zonaFria;

    @Enumerated(EnumType.STRING)
    @Column(name = "calidad_aislamiento", length = 20)
    private CalidadAislamiento calidadAislamiento;

    @Enumerated(EnumType.STRING)
    @Column(name = "fuente_calefaccion", length = 20)
    private FuenteEnergia fuenteCalefaccion;

    @Enumerated(EnumType.STRING)
    @Column(name = "fuente_agua_caliente", length = 20)
    private FuenteEnergia fuenteAguaCaliente;

    @Enumerated(EnumType.STRING)
    @Column(name = "categoria", nullable = false, length = 20)
    private CategoriaConsumo categoria;

    @Column(name = "probabilidad", nullable = false)
    private Double probabilidad;

    @Column(name = "costo_estimado_mensual", nullable = false)
    private BigDecimal costoEstimadoMensual;

    @ElementCollection
    @CollectionTable(name = "analisis_energetico_recomendaciones", joinColumns = @JoinColumn(name = "analisis_id"))
    @OrderColumn(name = "orden")
    @Column(name = "recomendacion", nullable = false, length = 255)
    private List<String> recomendaciones;

    @Builder
    private AnalisisEnergeticoEntity(LocalDateTime fecha, Double consumoKwh, Integer cantidadEquipos,
            TipoInmueble tipoInmueble, Boolean usoHorarioPico, Integer horasAltoConsumo, Integer metrosCuadrados,
            Integer antiguedadVivienda, Boolean zonaFria, CalidadAislamiento calidadAislamiento,
            FuenteEnergia fuenteCalefaccion, FuenteEnergia fuenteAguaCaliente, CategoriaConsumo categoria,
            Double probabilidad, BigDecimal costoEstimadoMensual, List<String> recomendaciones) {
        this.fecha = fecha;
        this.consumoKwh = consumoKwh;
        this.cantidadEquipos = cantidadEquipos;
        this.tipoInmueble = tipoInmueble;
        this.usoHorarioPico = usoHorarioPico;
        this.horasAltoConsumo = horasAltoConsumo;
        this.metrosCuadrados = metrosCuadrados;
        this.antiguedadVivienda = antiguedadVivienda;
        this.zonaFria = zonaFria;
        this.calidadAislamiento = calidadAislamiento;
        this.fuenteCalefaccion = fuenteCalefaccion;
        this.fuenteAguaCaliente = fuenteAguaCaliente;
        this.categoria = categoria;
        this.probabilidad = probabilidad;
        this.costoEstimadoMensual = costoEstimadoMensual;
        this.recomendaciones = recomendaciones == null ? new ArrayList<>() : new ArrayList<>(recomendaciones);
    }
}
