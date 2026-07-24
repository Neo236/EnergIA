package com.energiai.exception;

import java.util.List;

import com.energiai.dto.DatosErrorRespuesta;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.validation.BindingResult;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

class GlobalExceptionHandlerTest {

    private GlobalExceptionHandler exceptionHandler;

    @BeforeEach
    void setUp() {
        exceptionHandler = new GlobalExceptionHandler();
    }

    @Test
    void cuandoOcurreErrorDeValidacion_retornaRespuestaUniforme400() {
        BindingResult bindingResult = mock(BindingResult.class);
        FieldError fieldError = new FieldError("datosRegistroConsumo", "consumo", "debe ser mayor que 0");
        when(bindingResult.getFieldErrors()).thenReturn(List.of(fieldError));

        MethodArgumentNotValidException ex = new MethodArgumentNotValidException(null, bindingResult);

        ResponseEntity<DatosErrorRespuesta> response = exceptionHandler.manejarValidaciones(ex);

        assertEquals(HttpStatus.BAD_REQUEST, response.getStatusCode());
        assertNotNull(response.getBody());
        assertEquals(400, response.getBody().status());
        assertEquals("BAD_REQUEST", response.getBody().error());
        assertEquals("Errores de validacion en los datos de entrada", response.getBody().mensaje());
        assertEquals(1, response.getBody().detalles().size());
        assertEquals("consumo", response.getBody().detalles().get(0).campo());
    }

    @Test
    void cuandoJsonEsInvalido_retornaRespuestaUniforme400() {
        HttpMessageNotReadableException ex = new HttpMessageNotReadableException("JSON invalido", (org.springframework.http.HttpInputMessage) null);

        ResponseEntity<DatosErrorRespuesta> response = exceptionHandler.manejarJsonInvalido(ex);

        assertEquals(HttpStatus.BAD_REQUEST, response.getStatusCode());
        assertNotNull(response.getBody());
        assertEquals(400, response.getBody().status());
        assertEquals("El cuerpo de la solicitud (JSON) es invalido o esta ausente", response.getBody().mensaje());
    }

    @Test
    void cuandoRecursoNoExiste_retornaRespuestaUniforme404() {
        RecursoNoEncontradoException ex = new RecursoNoEncontradoException("Analisis no encontrado con ID 1");

        ResponseEntity<DatosErrorRespuesta> response = exceptionHandler.manejarRecursoNoEncontrado(ex);

        assertEquals(HttpStatus.NOT_FOUND, response.getStatusCode());
        assertNotNull(response.getBody());
        assertEquals(404, response.getBody().status());
        assertEquals("Analisis no encontrado con ID 1", response.getBody().mensaje());
    }

    @Test
    void cuandoOcurreErrorInterno_retornaRespuestaUniforme500() {
        Exception ex = new RuntimeException("Error inesperado de base de datos");

        ResponseEntity<DatosErrorRespuesta> response = exceptionHandler.manejarErrorInterno(ex, null);

        assertEquals(HttpStatus.INTERNAL_SERVER_ERROR, response.getStatusCode());
        assertNotNull(response.getBody());
        assertEquals(500, response.getBody().status());
        assertEquals("Ocurrio un error interno en el servidor. Por favor, intente mas tarde.", response.getBody().mensaje());
    }
}
