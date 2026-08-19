package com.energiai.health;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;
import org.springframework.boot.health.contributor.Health;
import org.springframework.boot.health.contributor.Status;

class VerificadorMotorPersistenciaTest {

    // El DataSource no se usa en estos casos: evaluar() recibe ya resuelto el
    // nombre del motor, que es la decision que interesa fijar.
    private VerificadorMotorPersistencia conExigencia(boolean exigePostgres) {
        return new VerificadorMotorPersistencia(null, exigePostgres);
    }

    @Test
    void aceptaPostgresCuandoElPerfilProdLoExige() {
        Health salud = conExigencia(true).evaluar("PostgreSQL");

        assertEquals(Status.UP, salud.getStatus());
        assertEquals("PostgreSQL", salud.getDetails().get("motor"));
    }

    // El caso que motivo el indicador: produccion sirviendo sobre H2 en memoria
    // mientras todas las sondas respondian UP.
    @Test
    void rechazaH2CuandoElPerfilProdExigePostgres() {
        Health salud = conExigencia(true).evaluar("H2");

        assertEquals(Status.DOWN, salud.getStatus());
        assertEquals("H2", salud.getDetails().get("motor"));
        assertEquals("PostgreSQL", salud.getDetails().get("esperado"));
    }

    // Sin perfil prod (la suite corre asi) H2 es legitimo y no debe ensuciar
    // readiness, o cada test de contexto empezaria a fallar.
    @Test
    void aceptaH2CuandoNoSeExigePostgres() {
        Health salud = conExigencia(false).evaluar("H2");

        assertEquals(Status.UP, salud.getStatus());
        assertEquals("omitida (perfil prod inactivo)", salud.getDetails().get("verificacion"));
    }

    // El driver podria capitalizar distinto en una version futura; la
    // comparacion no debe depender de eso.
    @Test
    void reconoceElMotorSinImportarLaCapitalizacion() {
        assertEquals(Status.UP, conExigencia(true).evaluar("postgresql").getStatus());
        assertEquals(Status.UP, conExigencia(true).evaluar("POSTGRESQL").getStatus());
    }

    // getDatabaseProductName() no deberia devolver null, pero un driver
    // exotico no puede tumbar la sonda con un NullPointerException.
    @Test
    void trataUnMotorNuloComoNoValido() {
        Health salud = conExigencia(true).evaluar(null);

        assertEquals(Status.DOWN, salud.getStatus());
        assertEquals("desconocido", salud.getDetails().get("motor"));
    }
}
