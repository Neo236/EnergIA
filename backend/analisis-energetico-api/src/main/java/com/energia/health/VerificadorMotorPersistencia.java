package com.energia.health;

import java.sql.Connection;
import java.sql.SQLException;
import java.util.Locale;
import java.util.concurrent.atomic.AtomicBoolean;

import javax.sql.DataSource;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.health.contributor.Health;
import org.springframework.boot.health.contributor.HealthIndicator;
import org.springframework.core.env.Environment;
import org.springframework.stereotype.Component;

// Verifica QUE MOTOR hay del otro lado del pool, no solo que haya alguno.
//
// El indicador `db` que trae Actuator responde UP con cualquier DataSource que
// conteste, incluida una H2 en memoria. Eso no es teorico: entre el 09/08 y el
// 18/08/2026 el backend de produccion corrio contra `jdbc:h2:mem:` porque su
// contenedor era anterior a que existiera Postgres en el compose y nunca se
// recreo. Durante nueve dias /actuator/health respondio {"status":"UP"}, el
// HEALTHCHECK del contenedor lo dio por sano y el CD certifico cada deploy:
// ninguna sonda miraba el motor, asi que todo analisis "persistido" vivia en el
// heap de la JVM y se perdia en cada reinicio.
//
// Este indicador cierra ese agujero. Va incluido en el grupo readiness (ver
// application.properties), de modo que un ambiente con el motor equivocado
// falla el gate del CD y dispara el rollback automatico en lugar de quedar
// certificado en verde.
@Component("motorPersistencia")
public class VerificadorMotorPersistencia implements HealthIndicator {

    private static final Logger log = LoggerFactory.getLogger(VerificadorMotorPersistencia.class);

    // getDatabaseProductName() devuelve "PostgreSQL" en el driver oficial. Se
    // compara en minusculas y por prefijo para no atarse a como lo capitalice
    // una version futura del driver.
    private static final String MOTOR_REQUERIDO = "postgresql";

    private final DataSource dataSource;
    private final boolean exigePostgres;

    // Solo los ambientes desplegados corren con el perfil prod (lo fija
    // SPRING_PROFILES_ACTIVE en docker-compose.yml, tanto en staging como en
    // produccion). La suite de tests corre sin perfil y sobre H2 a proposito,
    // asi que ahi la exigencia no aplica.
    //
    // La verificacion se gobierna por este flag y NO por @Profile sobre la
    // clase: el bean tiene que existir siempre, porque
    // `management.endpoint.health.group.readiness.include` lo nombra y Spring
    // rechaza el arranque si un grupo referencia un contribuidor inexistente.
    // @Autowired explicito: hay dos constructores y, sin la anotacion, Spring
    // no elige - busca uno sin argumentos y falla el arranque del contexto.
    @Autowired
    public VerificadorMotorPersistencia(DataSource dataSource, Environment entorno) {
        this(dataSource, entorno.matchesProfiles("prod"));
    }

    VerificadorMotorPersistencia(DataSource dataSource, boolean exigePostgres) {
        this.dataSource = dataSource;
        this.exigePostgres = exigePostgres;
    }

    @Override
    public Health health() {
        String motor;
        try (Connection conexion = dataSource.getConnection()) {
            motor = conexion.getMetaData().getDatabaseProductName();
        } catch (SQLException e) {
            // Igual que evaluar(): si el perfil prod no exige Postgres (tests,
            // entornos locales sobre H2), un fallo de conexion tampoco es motivo
            // para tumbar el readiness de este indicador - esa senal ya la da
            // el indicador `db`. Sin este chequeo, un hipo transitorio de la
            // base en un ambiente no-prod bajaba el readiness por una razon
            // que el resto de esta clase dice explicitamente que no aplica ahi.
            if (!exigePostgres) {
                return Health.up()
                        .withDetail("motor", "desconocido")
                        .withDetail("verificacion", "omitida (perfil prod inactivo): no se pudo determinar el motor")
                        .build();
            }
            // Sin conexion no hay nada que identificar. El indicador `db` ya
            // reporta la caida; aca solo se declara desconocido el motor.
            return Health.down(e).withDetail("motor", "desconocido").build();
        }
        return evaluar(motor);
    }

    // Separado de health() para poder ejercitar la decision sin una base real.
    Health evaluar(String motorDetectado) {
        String motor = motorDetectado == null ? "desconocido" : motorDetectado;
        boolean esPostgres = motor.toLowerCase(Locale.ROOT).startsWith(MOTOR_REQUERIDO);

        if (!exigePostgres) {
            return Health.up()
                    .withDetail("motor", motor)
                    .withDetail("verificacion", "omitida (perfil prod inactivo)")
                    .build();
        }
        if (esPostgres) {
            return Health.up().withDetail("motor", motor).build();
        }

        avisarUnaVez(motor);
        return Health.down()
                .withDetail("motor", motor)
                .withDetail("esperado", "PostgreSQL")
                .withDetail("causa", "el perfil prod exige PostgreSQL; no hay persistencia real")
                .build();
    }

    // show-details=when-authorized oculta el detalle en la respuesta HTTP, y sin
    // Spring Security en el classpath nadie llega a estar autorizado. Sin este
    // log, el operador ve un readiness en DOWN y ningun motivo. Se avisa una
    // sola vez porque el HEALTHCHECK del contenedor consulta cada 30 s y un
    // ERROR repetido cada media hora de ambiente roto solo tapa el resto.
    private final AtomicBoolean yaAvisado = new AtomicBoolean(false);

    private void avisarUnaVez(String motor) {
        if (yaAvisado.compareAndSet(false, true)) {
            log.error("Motor de persistencia inesperado: se detecto '{}' y el perfil prod exige PostgreSQL. "
                    + "Los datos NO se estan persistiendo de forma durable. "
                    + "Revisar que el servicio db este levantado y que DB_URL llegue al contenedor.", motor);
        }
    }
}
