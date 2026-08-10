package com.energiai.entity;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

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
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.OrderColumn;
import jakarta.persistence.SequenceGenerator;
import jakarta.persistence.Table;

// Persiste tanto los datos de entrada como el resultado de cada analisis.
// Los enums se guardan como texto (EnumType.STRING) para que la tabla no
// dependa del orden de declaracion en el codigo.
@Entity
@Table(name = "analisis_energetico")
public class AnalisisEnergeticoEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "analisis_energetico_seq")
    @SequenceGenerator(name = "analisis_energetico_seq", sequenceName = "analisis_energetico_seq", allocationSize = 1)
    private Long id;

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
    private List<String> recomendaciones = new ArrayList<>();

    protected AnalisisEnergeticoEntity() {
        // Requerido por JPA.
    }

    public AnalisisEnergeticoEntity(LocalDateTime fecha, Double consumoKwh, Integer cantidadEquipos,
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

    public Long getId() {
        return id;
    }

    public LocalDateTime getFecha() {
        return fecha;
    }

    public Double getConsumoKwh() {
        return consumoKwh;
    }

    public Integer getCantidadEquipos() {
        return cantidadEquipos;
    }

    public TipoInmueble getTipoInmueble() {
        return tipoInmueble;
    }

    public Boolean getUsoHorarioPico() {
        return usoHorarioPico;
    }

    public Integer getHorasAltoConsumo() {
        return horasAltoConsumo;
    }

    public Integer getMetrosCuadrados() {
        return metrosCuadrados;
    }

    public Integer getAntiguedadVivienda() {
        return antiguedadVivienda;
    }

    public Boolean getZonaFria() {
        return zonaFria;
    }

    public CalidadAislamiento getCalidadAislamiento() {
        return calidadAislamiento;
    }

    public FuenteEnergia getFuenteCalefaccion() {
        return fuenteCalefaccion;
    }

    public FuenteEnergia getFuenteAguaCaliente() {
        return fuenteAguaCaliente;
    }

    public CategoriaConsumo getCategoria() {
        return categoria;
    }

    public Double getProbabilidad() {
        return probabilidad;
    }

    public BigDecimal getCostoEstimadoMensual() {
        return costoEstimadoMensual;
    }

    public List<String> getRecomendaciones() {
        return recomendaciones;
    }
}
