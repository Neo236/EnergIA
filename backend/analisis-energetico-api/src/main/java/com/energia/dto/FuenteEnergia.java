package com.energia.dto;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonValue;

public enum FuenteEnergia {
    SOLAR("Solar"),
    ELECTRICIDAD("Electricidad"),
    OTROS("Otros");

    private final String descripcion;

    FuenteEnergia(String descripcion){
        this.descripcion = descripcion;
    }

    @JsonValue
    public String getDescripcion(){
        return descripcion;
    }

    @JsonCreator
    public static FuenteEnergia fromValue(String value) {
        if (value == null || value.isBlank()) {
            return null;
        }
        for (FuenteEnergia item : FuenteEnergia.values()) {
            if (item.name().equalsIgnoreCase(value) || item.descripcion.equalsIgnoreCase(value)) {
                return item;
            }
        }
        throw new IllegalArgumentException("Fuente de energía no válida: " + value);
    }
}