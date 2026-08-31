package com.energia.entity;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.HashSet;
import java.util.Set;
import java.util.UUID;

import org.junit.jupiter.api.Test;

class UuidV7GeneratorTest {

    @Test
    void generaUnUuidConVersionYVarianteCorrectas() {
        UUID id = UuidV7Generator.generate();

        assertEquals(7, id.version());
        assertEquals(2, id.variant());
    }

    @Test
    void noGeneraColisionesEnUnLote() {
        Set<UUID> generados = new HashSet<>();
        for (int i = 0; i < 10_000; i++) {
            assertTrue(generados.add(UuidV7Generator.generate()));
        }
    }

    @Test
    void elOrdenLexicograficoSigueElOrdenDeCreacion() throws InterruptedException {
        UUID primero = UuidV7Generator.generate();
        Thread.sleep(2);
        UUID segundo = UuidV7Generator.generate();

        assertTrue(primero.toString().compareTo(segundo.toString()) < 0);
    }
}
