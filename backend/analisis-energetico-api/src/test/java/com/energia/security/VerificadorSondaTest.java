package com.energia.security;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.Test;

class VerificadorSondaTest {

    @Test
    void reconoceLaCabeceraCuandoCoincideConElTokenConfigurado() {
        VerificadorSonda verificador = new VerificadorSonda("token-correcto");

        assertTrue(verificador.esSonda("token-correcto"));
    }

    @Test
    void noReconoceUnaCabeceraQueNoCoincide() {
        VerificadorSonda verificador = new VerificadorSonda("token-correcto");

        assertFalse(verificador.esSonda("token-incorrecto"));
    }

    @Test
    void noReconoceCuandoNoLlegaCabecera() {
        VerificadorSonda verificador = new VerificadorSonda("token-correcto");

        assertFalse(verificador.esSonda(null));
    }

    // Sin token configurado (caso por defecto en entornos sin la variable de
    // entorno, como local o CI de unit tests), ninguna peticion puede pasar
    // por sonda - ni siquiera una cabecera vacia contra un token vacio.
    @Test
    void noReconoceNadaCuandoNoHayTokenConfigurado() {
        VerificadorSonda verificador = new VerificadorSonda("");

        assertFalse(verificador.esSonda(""));
        assertFalse(verificador.esSonda(null));
        assertFalse(verificador.esSonda("cualquier-cosa"));
    }

    @Test
    void noReconoceUnaCabeceraVaciaAunConTokenConfigurado() {
        VerificadorSonda verificador = new VerificadorSonda("token-correcto");

        assertFalse(verificador.esSonda(""));
    }
}
