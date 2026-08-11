package com.energiai.security;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

// Distingue las peticiones de verificacion automatica (CI/CD, ver
// verificacion-sistema.yml) de un analisis real, para que las primeras no se
// persistan. El token viaja en la cabecera X-EnergiAI-Sonda y NUNCA debe
// habilitar nada mas que eso: ni autorizacion ni limites de uso. Si en algun
// momento existiera un limite de peticiones, tiene que aplicarse por igual a
// las peticiones marcadas como sonda - de lo contrario, esta marca deja de
// ser un detalle de persistencia/telemetria y pasa a ser una llave para
// saltear ese limite, y filtrarla deja de ser inofensivo.
@Component
public class VerificadorSonda {

    private final byte[] tokenConfigurado;

    public VerificadorSonda(@Value("${sonda.token:}") String tokenConfigurado) {
        this.tokenConfigurado = tokenConfigurado.getBytes(StandardCharsets.UTF_8);
    }

    // Sin token configurado, ninguna cabecera puede considerarse una sonda -
    // ni siquiera una vacia: si comparara vacio contra vacio, cualquiera que
    // omitiera la cabecera pasaria la verificacion.
    public boolean esSonda(String cabeceraRecibida) {
        if (tokenConfigurado.length == 0 || cabeceraRecibida == null || cabeceraRecibida.isEmpty()) {
            return false;
        }
        byte[] recibido = cabeceraRecibida.getBytes(StandardCharsets.UTF_8);
        return MessageDigest.isEqual(tokenConfigurado, recibido);
    }
}
