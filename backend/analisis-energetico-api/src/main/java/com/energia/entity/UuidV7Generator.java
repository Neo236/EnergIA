package com.energia.entity;

import java.security.SecureRandom;
import java.util.UUID;

import org.hibernate.engine.spi.SharedSessionContractImplementor;
import org.hibernate.id.IdentifierGenerator;

// Genera UUIDs version 7 (RFC 9562): timestamp de milisegundos en los primeros
// 48 bits + el resto aleatorio. A diferencia de un id secuencial (adivinable,
// requiere una secuencia central que coordinar si la DB se particiona) o un
// UUID v4 puro (aleatorio de punta a punta, fragmenta el indice porque cada
// insert cae en una pagina distinta), v7 no es adivinable, no necesita
// coordinacion para generarse, y mantiene el orden de insercion en el indice
// porque el timestamp va primero. Java todavia no lo genera nativo (solo v3/
// v4/v5 via UUID.randomUUID()/nameUUIDFromBytes()), de ahi este generador.
//
// El id se genera aca (en la app), no en la base: es el mismo motivo por el
// que se eligio Postgres pensando en portar a Oracle mas adelante - Oracle no
// tiene un tipo UUID nativo (se guardaria en RAW(16) o VARCHAR2(36) via
// SYS_GUID()), pero si el id ya lo genera Java antes del insert, migrar de
// motor no depende de esa diferencia en absoluto.
public class UuidV7Generator implements IdentifierGenerator {

    private static final SecureRandom RANDOM = new SecureRandom();

    @Override
    public Object generate(SharedSessionContractImplementor session, Object object) {
        return generate();
    }

    public static UUID generate() {
        byte[] value = new byte[16];
        RANDOM.nextBytes(value);

        long timestamp = System.currentTimeMillis();
        value[0] = (byte) (timestamp >>> 40);
        value[1] = (byte) (timestamp >>> 32);
        value[2] = (byte) (timestamp >>> 24);
        value[3] = (byte) (timestamp >>> 16);
        value[4] = (byte) (timestamp >>> 8);
        value[5] = (byte) timestamp;

        value[6] = (byte) (0x70 | (value[6] & 0x0F)); // version 7
        value[8] = (byte) (0x80 | (value[8] & 0x3F)); // variante 10xxxxxx

        long mostSigBits = 0;
        for (int i = 0; i < 8; i++) {
            mostSigBits = (mostSigBits << 8) | (value[i] & 0xFF);
        }
        long leastSigBits = 0;
        for (int i = 8; i < 16; i++) {
            leastSigBits = (leastSigBits << 8) | (value[i] & 0xFF);
        }
        return new UUID(mostSigBits, leastSigBits);
    }
}
