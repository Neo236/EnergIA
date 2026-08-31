package com.energia.service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import com.energia.dto.CategoriaConsumo;
import com.energia.dto.DatosRegistroAnalisis;
import com.energia.dto.TipoInmueble;
import com.energia.entity.AnalisisEnergeticoEntity;
import com.energia.exception.RecursoNoEncontradoException;
import com.energia.repository.AnalisisEnergeticoRepository;

// Deliberadamente @SpringBootTest y NO @DataJpaTest: @DataJpaTest envuelve
// todo el metodo de test en una unica transaccion, lo que esconde el bug real
// que este test verifica. En produccion, obtenerAnalisisPorId() abre y CIERRA
// su propia transaccion (@Transactional en el service) antes de que el
// controller serialice la respuesta - si "recomendaciones" (coleccion LAZY)
// no queda materializada antes de ese cierre, Hibernate tira
// LazyInitializationException recien al armar el JSON. Se detecto asi en
// verificacion manual contra Postgres real con open-in-view=false (que es lo
// que hoy tapaba el bug en produccion): un simple entidad.getRecomendaciones()
// no alcanza, hace falta forzar la lectura (paraDto copia a ArrayList) dentro
// de la transaccion.
@SpringBootTest(properties = {
        "spring.datasource.url=jdbc:h2:mem:analisis-service-it;DB_CLOSE_DELAY=-1",
        "spring.datasource.username=sa",
        "spring.datasource.password=",
        "spring.flyway.enabled=false",
        "spring.jpa.hibernate.ddl-auto=create-drop"
})
class AnalisisEnergeticoServiceIntegrationTest {

    @Autowired
    private AnalisisEnergeticoService service;

    @Autowired
    private AnalisisEnergeticoRepository repository;

    @Test
    void obtenerAnalisisPorId_devuelveRecomendacionesFueraDeLaTransaccionDeLectura() {
        AnalisisEnergeticoEntity guardado = repository.save(AnalisisEnergeticoEntity.builder()
                .fecha(LocalDateTime.of(2026, 8, 10, 11, 45))
                .consumoKwh(450.5)
                .cantidadEquipos(8)
                .tipoInmueble(TipoInmueble.CASA)
                .horasAltoConsumo(6)
                .categoria(CategoriaConsumo.EFICIENTE)
                .probabilidad(0.25)
                .costoEstimadoMensual(BigDecimal.valueOf(337.87))
                .recomendaciones(List.of("Mantener los habitos actuales de ahorro."))
                .build());

        // obtenerAnalisisPorId ya termino (y cerro su transaccion) para cuando
        // llegamos aca: esta lectura ocurre fuera de cualquier sesion de
        // Hibernate, igual que la serializacion JSON en el controller real.
        DatosRegistroAnalisis resultado = service.obtenerAnalisisPorId(guardado.getId());

        assertEquals(List.of("Mantener los habitos actuales de ahorro."), resultado.recomendaciones());
    }

    @Test
    void obtenerAnalisisPorId_lanzaRecursoNoEncontradoCuandoNoExiste() {
        UUID idInexistente = UUID.randomUUID();
        assertTrue(repository.findById(idInexistente).isEmpty());

        RecursoNoEncontradoException ex = assertThrows(RecursoNoEncontradoException.class,
                () -> service.obtenerAnalisisPorId(idInexistente));
        assertEquals("Analisis no encontrado con ID " + idInexistente, ex.getMessage());
    }
}
