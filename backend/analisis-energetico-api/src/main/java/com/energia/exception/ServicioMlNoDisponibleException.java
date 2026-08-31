package com.energia.exception;

public class ServicioMlNoDisponibleException extends RuntimeException {
    
    public ServicioMlNoDisponibleException(String mensaje) {
        super(mensaje);
    }

    public ServicioMlNoDisponibleException(String mensaje, Throwable causa){
        super(mensaje, causa);
    }
}