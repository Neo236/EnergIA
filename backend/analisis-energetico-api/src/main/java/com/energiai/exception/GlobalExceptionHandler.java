package com.energiai.exception;

import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import com.energiai.dto.DatosErrorCampo;
import com.energiai.dto.DatosErrorRespuesta;

import jakarta.servlet.http.HttpServletRequest;

@RestControllerAdvice
public class GlobalExceptionHandler {

    /**
     * Manejo de validaciones de DTO (@Valid).
     * Devuelve HTTP 400 Bad Request con el detalle de cada campo invalido o ausente.
     */
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<DatosErrorRespuesta> manejarValidaciones(MethodArgumentNotValidException ex) {
        List<DatosErrorCampo> erroresCampos = ex.getBindingResult()
                .getFieldErrors()
                .stream()
                .map(err -> new DatosErrorCampo(err.getField(), err.getDefaultMessage()))
                .toList();

        DatosErrorRespuesta respuesta = DatosErrorRespuesta.de(
                HttpStatus.BAD_REQUEST.value(),
                HttpStatus.BAD_REQUEST.name(),
                "Errores de validacion en los datos de entrada",
                erroresCampos
        );

        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(respuesta);
    }

    /**
     * Manejo de JSON mal formado o cuerpo de solicitud ausente.
     * Devuelve HTTP 400 Bad Request.
     */
    @ExceptionHandler(HttpMessageNotReadableException.class)
    public ResponseEntity<DatosErrorRespuesta> manejarJsonInvalido(HttpMessageNotReadableException ex) {
        DatosErrorRespuesta respuesta = DatosErrorRespuesta.de(
                HttpStatus.BAD_REQUEST.value(),
                HttpStatus.BAD_REQUEST.name(),
                "El cuerpo de la solicitud (JSON) es invalido o esta ausente"
        );

        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(respuesta);
    }

    /**
     * Manejo de recursos inexistentes planteados por la logica de negocio.
     * Devuelve HTTP 404 Not Found.
     */
    @ExceptionHandler(RecursoNoEncontradoException.class)
    public ResponseEntity<DatosErrorRespuesta> manejarRecursoNoEncontrado(RecursoNoEncontradoException ex) {
        DatosErrorRespuesta respuesta = DatosErrorRespuesta.de(
                HttpStatus.NOT_FOUND.value(),
                HttpStatus.NOT_FOUND.name(),
                ex.getMessage()
        );

        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(respuesta);
    }

    /**
     * Manejo global de errores internos no controlados.
     * Devuelve HTTP 500 Internal Server Error.
     */
    @ExceptionHandler(Exception.class)
    public ResponseEntity<DatosErrorRespuesta> manejarErrorInterno(Exception ex, HttpServletRequest request) {
        DatosErrorRespuesta respuesta = DatosErrorRespuesta.de(
                HttpStatus.INTERNAL_SERVER_ERROR.value(),
                HttpStatus.INTERNAL_SERVER_ERROR.name(),
                "Ocurrio un error interno en el servidor. Por favor, intente mas tarde."
        );

        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(respuesta);
    }
}
