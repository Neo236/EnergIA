package com.energia.client;                                                                                                                                                  
                                                                                                                                                                                  
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestClientResponseException;
import org.springframework.web.client.ResourceAccessException;

import com.energia.dto.DatosRegistroAnalisis;
import com.energia.dto.DatosRegistroConsumo;
import com.energia.exception.DatosEntradaInvalidosException;
import com.energia.exception.MlRespuestaInvalidaException;
import com.energia.exception.ServicioMlNoDisponibleException;
                                                                                                                                                                                  
@Component                                                                                                                                                                    
public class MlClient {                                                                                                                                                       
                                                                                                                                                                                  
    private final RestClient restClient;                                                                                                                                      
    private final String mlServiceUrl;                                                                                                                                        
                                                                                                                                                                                                                                                                                        
    public MlClient(RestClient restClient, @Value("${ml.service.url:http://localhost:8000}") String mlServiceUrl) {                                                           
        this.restClient = restClient;                                                                                                                                         
        this.mlServiceUrl = mlServiceUrl;                                                                                                                                     
    }                                                                                                                                                                                                                                                                                                                                          
    public DatosRegistroAnalisis predecir(DatosRegistroConsumo datos) {
        // =====================================================================
        // IMPLEMENTACIÓN ANTERIOR (comentada como referencia):
        // convertía CUALQUIER error en 503, sin distinguir el tipo de falla.
        //
        // try {
        //     return restClient.post()
        //             .uri(mlServiceUrl + "/analisis-energetico")
        //             .contentType(MediaType.APPLICATION_JSON)
        //             .body(datos)
        //             .retrieve()
        //             .body(DatosRegistroAnalisis.class);
        // } catch (Exception e) {
        //     throw new ServicioMlNoDisponibleException("El servicio Machine Learning no se encuentra disponible");
        // }
        // =====================================================================

        try {
            return restClient.post()
                    .uri(mlServiceUrl + "/analisis-energetico")
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(datos)
                    .retrieve()
                    .body(DatosRegistroAnalisis.class);
        } catch (RestClientResponseException e) {
            // FastAPI respondió con un código HTTP de error.
            // 4xx (ej: 422 validación de entrada) => el back-end la expone como 400.
            if (e.getStatusCode().is4xxClientError()) {
                throw new DatosEntradaInvalidosException(
                        "El servicio de Machine Learning rechazó los datos de entrada (HTTP "
                                + e.getStatusCode().value() + ")"
                );
            }
            // 5xx (ej: 503 del ML) => el servicio está caído o no disponible.
            throw new ServicioMlNoDisponibleException(
                    "El servicio Machine Learning no se encuentra disponible");
        } catch (ResourceAccessException e) {
            // Error de conexión o timeout.
            throw new ServicioMlNoDisponibleException(
                    "El servicio Machine Learning no se encuentra disponible");
        } catch (RestClientException e) {
            // Respuesta inesperada o inválida (JSON no deserializable, estructura rara, etc.).
            throw new MlRespuestaInvalidaException(
                    "El servicio Machine Learning devolvió una respuesta inesperada o inválida");
        }
    }
}