package com.energia.dto;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonValue;

public enum CalidadAislamiento {
    MUYALTA("Muy Alta"),
    ALTA("Alta"),
    MEDIA("Media"),
    BAJA("Baja"),
    MUYBAJA("Muy Baja");

    private final String descripcion;

    CalidadAislamiento(String descripcion){
        this.descripcion = descripcion;
    }

    @JsonValue
    public String getDescripcion(){
        return descripcion;
    }

    @JsonCreator
    public static CalidadAislamiento fromValue(String value) {
        if (value == null || value.isBlank()) {
            return null;
        }
        for (CalidadAislamiento item : CalidadAislamiento.values()) {
            if (item.name().equalsIgnoreCase(value) || item.descripcion.equalsIgnoreCase(value)) {
                return item;
            }
        }
        throw new IllegalArgumentException("Calidad de aislamiento no válida: " + value);
    }
}