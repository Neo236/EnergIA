package com.energiai.repository;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.data.jpa.test.autoconfigure.DataJpaTest;

import com.energiai.dto.CategoriaConsumo;
import com.energiai.dto.TipoInmueble;
import com.energiai.entity.AnalisisEnergeticoEntity;

// Flyway no corre en este slice de test (usa la base H2 embebida que
// @DataJpaTest arma sola); el esquema lo genera Hibernate a partir de las
// mismas anotaciones de la entidad, que es justo lo que este test valida.
@DataJpaTest(properties = {
        "spring.flyway.enabled=false",
        "spring.jpa.hibernate.ddl-auto=create-drop"
})
class AnalisisEnergeticoRepositoryTest {

    @Autowired
    private AnalisisEnergeticoRepository repository;

    private AnalisisEnergeticoEntity nuevoAnalisis() {
        return AnalisisEnergeticoEntity.builder()
                .fecha(LocalDateTime.of(2026, 8, 10, 11, 45))
                .consumoKwh(450.5)
                .cantidadEquipos(8)
                .tipoInmueble(TipoInmueble.CASA)
                .usoHorarioPico(true)
                .horasAltoConsumo(6)
                .metrosCuadrados(30)
                .antiguedadVivienda(34)
                .zonaFria(false)
                .categoria(CategoriaConsumo.EFICIENTE)
                .probabilidad(0.25)
                .costoEstimadoMensual(BigDecimal.valueOf(337.87))
                .recomendaciones(List.of("Mantener los hábitos actuales de ahorro."))
                .build();
    }

    @Test
    void guardaYRecuperaUnAnalisisPorId() {
        AnalisisEnergeticoEntity guardado = repository.save(nuevoAnalisis());

        assertNotNull(guardado.getId());

        Optional<AnalisisEnergeticoEntity> encontrado = repository.findById(guardado.getId());

        assertTrue(encontrado.isPresent());
        assertEquals(CategoriaConsumo.EFICIENTE, encontrado.get().getCategoria());
        assertEquals(List.of("Mantener los hábitos actuales de ahorro."), encontrado.get().getRecomendaciones());
    }

    @Test
    void devuelveVacioCuandoElIdNoExiste() {
        assertTrue(repository.findById(999999L).isEmpty());
    }
}
