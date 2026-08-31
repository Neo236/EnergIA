package com.energia.health;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.test.context.ActiveProfiles;

// Reproduce el incidente real: un backend con el perfil prod activo sirviendo
// sobre H2 en memoria. Entre el 09/08 y el 18/08/2026 produccion corrio
// exactamente asi y /actuator/health respondia UP, con lo cual el CD certifico
// nueve dias de deploys sin persistencia durable.
//
// Los tests unitarios de VerificadorMotorPersistencia fijan la decision; este
// verifica lo que de verdad importaba y no estaba cubierto: que esa decision
// llegue hasta /actuator/health/readiness, que es el endpoint que consultan el
// gate del CD y el HEALTHCHECK del contenedor. Un indicador correcto pero fuera
// del grupo readiness habria dejado el agujero abierto igual.
@SpringBootTest(
        webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
        properties = {
                "spring.datasource.url=jdbc:h2:mem:readiness-motor-it;DB_CLOSE_DELAY=-1",
                "spring.datasource.username=sa",
                "spring.datasource.password=",
                "spring.flyway.enabled=false",
                "spring.jpa.hibernate.ddl-auto=create-drop"
        })
@ActiveProfiles("prod")
class ReadinessMotorPersistenciaIntegrationTest {

    @LocalServerPort
    private int puerto;

    // TestRestTemplate ya no viene en spring-boot-test 4.x; el cliente del JDK
    // alcanza de sobra para leer un endpoint de salud y evita sumar una
    // dependencia solo para esto.
    private HttpResponse<String> consultar(String ruta) throws Exception {
        HttpRequest peticion = HttpRequest.newBuilder()
                .uri(URI.create("http://localhost:" + puerto + ruta))
                .GET()
                .build();
        return HttpClient.newHttpClient().send(peticion, HttpResponse.BodyHandlers.ofString());
    }

    @Test
    void readinessQuedaEnDownCuandoElMotorNoEsPostgres() throws Exception {
        HttpResponse<String> respuesta = consultar("/actuator/health/readiness");

        // Un grupo de salud en DOWN se sirve con 503, que es lo que hace fallar
        // el paso "Verificar salud" de cd-backend.yml y dispara el rollback.
        assertEquals(503, respuesta.statusCode());
        assertTrue(respuesta.body().contains("DOWN"),
                "readiness deberia reportar DOWN con H2 bajo el perfil prod, pero fue: " + respuesta.body());
    }

    // Contraste necesario: sin esto, un readiness roto por cualquier otro
    // motivo haria pasar el test de arriba por la razon equivocada.
    @Test
    void livenessSigueEnUpPorqueElProcesoEstaVivo() throws Exception {
        HttpResponse<String> respuesta = consultar("/actuator/health/liveness");

        assertEquals(200, respuesta.statusCode());
        assertTrue(respuesta.body().contains("UP"));
    }
}
