package com.energiai.security;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

// Distingue las peticiones de verificacion manual (curl documentado en
// docs/certificacion/README.md) de un analisis real, para que las primeras no
// se persistan. El token viaja en la cabecera X-EnergiAI-Sonda y NUNCA debe
// habilitar nada mas que eso: ni autorizacion ni limites de uso. Si en algun
// momento existiera un limite de peticiones, tiene que aplicarse por igual a
// las peticiones marcadas como sonda - de lo contrario, esta marca deja de
// ser un detalle de persistencia/telemetria y pasa a ser una llave para
// saltear ese limite, y filtrarla deja de ser inofensivo.
@Component
public class VerificadorSonda {

    private static final String ALGORITMO_HASH = "SHA-256";

    private final byte[] tokenConfigurado;
    // Se compara el hash de ambos lados, no los bytes crudos: MessageDigest.
    // isEqual solo es de tiempo constante cuando los dos arrays miden lo
    // mismo - si difieren, devuelve false de inmediato sin recorrerlos.
    // Hasheando primero, lo que se compara siempre mide 32 bytes sin
    // importar el largo real de la cabecera recibida, y esa longitud deja de
    // filtrarse por temporizacion.
    private final byte[] hashTokenConfigurado;

    public VerificadorSonda(@Value("${sonda.token:}") String tokenConfigurado) {
        this.tokenConfigurado = tokenConfigurado.getBytes(StandardCharsets.UTF_8);
        this.hashTokenConfigurado = hash(this.tokenConfigurado);
    }

    // Sin token configurado, ninguna cabecera puede considerarse una sonda -
    // ni siquiera una vacia: si comparara vacio contra vacio, cualquiera que
    // omitiera la cabecera pasaria la verificacion.
    public boolean esSonda(String cabeceraRecibida) {
        if (tokenConfigurado.length == 0 || cabeceraRecibida == null || cabeceraRecibida.isEmpty()) {
            return false;
        }
        byte[] recibido = cabeceraRecibida.getBytes(StandardCharsets.UTF_8);
        return MessageDigest.isEqual(hashTokenConfigurado, hash(recibido));
    }

    private static byte[] hash(byte[] valor) {
        try {
            return MessageDigest.getInstance(ALGORITMO_HASH).digest(valor);
        } catch (NoSuchAlgorithmException e) {
            // SHA-256 es obligatorio en toda implementacion de Java (JCA
            // "Standard Algorithm Names"), esto no deberia ocurrir nunca.
            throw new IllegalStateException("SHA-256 no disponible en este JDK", e);
        }
    }
}
