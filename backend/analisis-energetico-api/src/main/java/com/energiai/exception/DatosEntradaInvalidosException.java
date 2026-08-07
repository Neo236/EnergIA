package com.energiai.exception;

public class DatosEntradaInvalidosException extends RuntimeException {

    public DatosEntradaInvalidosException(String mensaje) {
        super(mensaje);
    }

    public DatosEntradaInvalidosException(String mensaje, Throwable causa) {
        super(mensaje, causa);
    }
}
