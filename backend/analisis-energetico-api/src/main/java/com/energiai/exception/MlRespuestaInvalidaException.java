package com.energiai.exception;

public class MlRespuestaInvalidaException extends RuntimeException {

    public MlRespuestaInvalidaException(String mensaje) {
        super(mensaje);
    }

    public MlRespuestaInvalidaException(String mensaje, Throwable causa) {
        super(mensaje, causa);
    }
}
