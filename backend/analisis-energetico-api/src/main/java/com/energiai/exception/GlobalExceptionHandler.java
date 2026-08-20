package com.energiai.exception;

import java.util.List;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException;
import org.springframework.web.servlet.resource.NoResourceFoundException;

import com.energiai.dto.DatosErrorCampo;
import com.energiai.dto.DatosErrorRespuesta;

import jakarta.servlet.http.HttpServletRequest;

@RestControllerAdvice
public class GlobalExceptionHandler {

    // Criterio de niveles, para que el log sirva de algo:
    //   warn  -> lo que el cliente o un servicio externo hicieron mal. Es
    //            esperable, se responde con un 4xx/5xx del contrato y no hay
    //            nada que arreglar en el codigo. Sin traza: una pila entera
    //            por cada 404 tapa lo que si importa.
    //   error -> lo que no esta previsto, es decir el catch-all. Ahi si va la
    //            traza completa, porque es el unico caso donde hay un bug
    //            propio que diagnosticar.
    // En ningun caso se loguea el cuerpo de la peticion: trae los datos del
    // inmueble que cargo el usuario.
    private static final Logger log = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    // Manejo de validaciones de DTO (@Valid).
    // Devuelve HTTP 400 Bad Request con el detalle de cada campo invalido o ausente.
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<DatosErrorRespuesta> manejarValidaciones(MethodArgumentNotValidException ex) {
        List<DatosErrorCampo> erroresCampos = ex.getBindingResult()
                .getFieldErrors()
                .stream()
                .map(err -> new DatosErrorCampo(err.getField(), err.getDefaultMessage()))
                .toList();

        log.warn("Validacion fallida en {} campo(s): {}",
                erroresCampos.size(),
                erroresCampos.stream().map(DatosErrorCampo::campo).toList());

        DatosErrorRespuesta respuesta = DatosErrorRespuesta.de(
                HttpStatus.BAD_REQUEST.value(),
                HttpStatus.BAD_REQUEST.name(),
                "Errores de validacion en los datos de entrada",
                erroresCampos
        );

        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(respuesta);
    }

    // Manejo de JSON mal formado o cuerpo de solicitud ausente.
    // Devuelve HTTP 400 Bad Request.
    @ExceptionHandler(HttpMessageNotReadableException.class)
    public ResponseEntity<DatosErrorRespuesta> manejarJsonInvalido(HttpMessageNotReadableException ex) {
        log.warn("Cuerpo de la solicitud ilegible: {}", ex.getMostSpecificCause().getMessage());

        DatosErrorRespuesta respuesta = DatosErrorRespuesta.de(
                HttpStatus.BAD_REQUEST.value(),
                HttpStatus.BAD_REQUEST.name(),
                "El formato de la solicitud (JSON) es invalido o esta ausente"
        );

        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(respuesta);
    }

    // Manejo de recursos inexistentes planteados por la logica de negocio.
    // Devuelve HTTP 404 Not Found.
    @ExceptionHandler(RecursoNoEncontradoException.class)
    public ResponseEntity<DatosErrorRespuesta> manejarRecursoNoEncontrado(RecursoNoEncontradoException ex) {
        log.warn("Recurso no encontrado: {}", ex.getMessage());

        DatosErrorRespuesta respuesta = DatosErrorRespuesta.de(
                HttpStatus.NOT_FOUND.value(),
                HttpStatus.NOT_FOUND.name(),
                ex.getMessage()
        );

        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(respuesta);
    }

    @ExceptionHandler(ServicioMlNoDisponibleException.class)
    public ResponseEntity<DatosErrorRespuesta> manejaServicioMlNoDisponible(ServicioMlNoDisponibleException ex) {
        // MlClient no loguea: sin esta linea, un ML caido no deja ningun
        // rastro en el backend y solo se ve como un 503 del lado del cliente.
        log.warn("El servicio de ML no esta disponible: {}", ex.getMessage());

        DatosErrorRespuesta respuesta = DatosErrorRespuesta.de(
            HttpStatus.SERVICE_UNAVAILABLE.value(),
            HttpStatus.SERVICE_UNAVAILABLE.name(),
            ex.getMessage()
        );
        return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body(respuesta);
    }

    // FastAPI rechazó los datos de entrada (4xx, ej: 422 de validación).
    // El back-end lo expone como 400 Bad Request.
    @ExceptionHandler(DatosEntradaInvalidosException.class)
    public ResponseEntity<DatosErrorRespuesta> manejarDatosEntradaInvalidos(DatosEntradaInvalidosException ex) {
        log.warn("El servicio de ML rechazo los datos de entrada: {}", ex.getMessage());

        DatosErrorRespuesta respuesta = DatosErrorRespuesta.de(
            HttpStatus.BAD_REQUEST.value(),
            HttpStatus.BAD_REQUEST.name(),
            ex.getMessage()
        );
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(respuesta);
    }

    // El servicio de ML devolvió una respuesta inesperada o inválida.
    // Se expone como 502 Bad Gateway (el upstream respondió de forma anómala).
    @ExceptionHandler(MlRespuestaInvalidaException.class)
    public ResponseEntity<DatosErrorRespuesta> manejarMlRespuestaInvalida(MlRespuestaInvalidaException ex) {
        log.warn("Respuesta invalida del servicio de ML: {}", ex.getMessage());

        DatosErrorRespuesta respuesta = DatosErrorRespuesta.de(
            HttpStatus.BAD_GATEWAY.value(),
            HttpStatus.BAD_GATEWAY.name(),
            ex.getMessage()
        );
        return ResponseEntity.status(HttpStatus.BAD_GATEWAY).body(respuesta);
    }

    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<DatosErrorRespuesta> manejarIllegalArgumentException(IllegalArgumentException ex) {
        log.warn("Argumento invalido: {}", ex.getMessage());

        DatosErrorRespuesta respuesta = DatosErrorRespuesta.de(
                HttpStatus.BAD_REQUEST.value(),
                HttpStatus.BAD_REQUEST.name(),
                ex.getMessage()
        );
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(respuesta);
    }

    // Un parametro de la ruta que no convierte al tipo que declara el
    // controlador. Hoy es un solo caso: GET /analisis-energetico/{id} con un
    // id que no parsea como UUID, tipico de un enlace cortado al copiarlo.
    //
    // Spring lanza esto ANTES de entrar al metodo, asi que la excepcion que
    // llega es MethodArgumentTypeMismatchException y no el
    // IllegalArgumentException("Invalid UUID string") que la origina. El
    // handler de arriba no la alcanza: el resolver busca por el tipo lanzado
    // y solo mira la cadena de causas si no encontro ningun handler, y
    // Exception.class siempre es un match. Sin este metodo, entonces, la
    // peticion terminaba en el catch-all y salia un 500.
    //
    // Se responde 404 y no 400 porque para quien consume la API el efecto es
    // el mismo que un id inexistente: no hay ningun analisis en esa URL. Ese
    // es ademas el estado que el front ya sabe explicar ("el enlace puede
    // estar incompleto"); con un 400 caeria en el mensaje generico de error.
    // El valor recibido va al log, no a la respuesta: no hace falta
    // devolverle al cliente el texto que acaba de mandar.
    @ExceptionHandler(MethodArgumentTypeMismatchException.class)
    public ResponseEntity<DatosErrorRespuesta> manejarParametroInvalido(MethodArgumentTypeMismatchException ex) {
        log.warn("Parametro '{}' con valor invalido: '{}'", ex.getName(), ex.getValue());

        DatosErrorRespuesta respuesta = DatosErrorRespuesta.de(
                HttpStatus.NOT_FOUND.value(),
                HttpStatus.NOT_FOUND.name(),
                "El recurso solicitado no fue encontrado"
        );
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(respuesta);
    }

    // Manejo global de errores internos no controlados.
    // Devuelve HTTP 500 Internal Server Error.
    @ExceptionHandler(Exception.class)
    public ResponseEntity<DatosErrorRespuesta> manejarErrorInterno(Exception ex, HttpServletRequest request) {
        // La respuesta al cliente es deliberadamente opaca, asi que sin esta
        // traza un 500 no deja forma de saber que fallo. Se registra la ruta,
        // no el cuerpo.
        //
        // El request puede venir nulo cuando se invoca el handler directo
        // desde una prueba unitaria. Una NPE aca convertiria el ultimo
        // recurso en un error sin formato y romperia el contrato de error
        // uniforme, justo en el camino que existe para sostenerlo.
        String ruta = request != null
                ? request.getMethod() + " " + request.getRequestURI()
                : "(sin request)";
        log.error("Error no controlado en {}", ruta, ex);

        DatosErrorRespuesta respuesta = DatosErrorRespuesta.de(
                HttpStatus.INTERNAL_SERVER_ERROR.value(),
                HttpStatus.INTERNAL_SERVER_ERROR.name(),
                "Ocurrio un error interno en el servidor. Por favor, intente mas tarde."
        );

        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(respuesta);
    }

     @ExceptionHandler(NoResourceFoundException.class)                                                                                                                             
    public ResponseEntity<DatosErrorRespuesta> manejarRutaNoEncontrada(NoResourceFoundException ex) {
        log.warn("Ruta inexistente: {}", ex.getResourcePath());

        DatosErrorRespuesta respuesta = DatosErrorRespuesta.de(                                                                                                          
                HttpStatus.NOT_FOUND.value(),                                                                                                                                     
                HttpStatus.NOT_FOUND.name(),                                                                                                                                      
                "La ruta solicitada no existe: " + ex.getResourcePath()                                                                                                           
        );                                                                                                                                                                        
                                                                                                                                                                                  
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(respuesta);                                                                                        
    }
}
