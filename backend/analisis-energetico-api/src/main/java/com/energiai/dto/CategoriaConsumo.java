package com.energiai.dto;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonValue;

public enum CategoriaConsumo {
    EFICIENTE("Eficiente"),
    MODERADO("Moderado"),
    INEFICIENTE("Ineficiente");

    private final String descripcion;

    CategoriaConsumo(String descripcion) {
        this.descripcion = descripcion;
    }

    @JsonValue
    public String getDescripcion() {
        return descripcion;
    }

    @JsonCreator
    public static CategoriaConsumo fromValue(String value) {
        if (value == null || value.isBlank()) {
            return null;
        }
        for (CategoriaConsumo item : CategoriaConsumo.values()) {
            if (item.name().equalsIgnoreCase(value) || item.descripcion.equalsIgnoreCase(value)) {
                return item;
            }
        }
        throw new IllegalArgumentException("Categoría de consumo no válida: " + value);
    }
}