package com.energiai.dto;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonValue;

public enum TipoInmueble {
    CASA("Casa"),
    DEPARTAMENTO("Departamento"),
    COMERCIO("Comercio"),
    PYME("Pyme");

    private final String descripcion;

    TipoInmueble(String descripcion) {
        this.descripcion = descripcion;
    }

    @JsonValue
    public String getDescripcion(){
        return descripcion;
    }

    @JsonCreator
    public static TipoInmueble fromValue(String value) {
        if (value == null || value.isBlank()) {
            return null;
        }
        for (TipoInmueble tipo : TipoInmueble.values()) {
            if (tipo.name().equalsIgnoreCase(value) || tipo.descripcion.equalsIgnoreCase(value)) {
                return tipo;
            }
        }
        throw new IllegalArgumentException("Tipo de inmueble no válido: " + value);
    }
}