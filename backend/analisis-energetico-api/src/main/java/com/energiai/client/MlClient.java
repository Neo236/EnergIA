package com.energiai.client;                                                                                                                                                  
                                                                                                                                                                                  
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import com.energiai.dto.DatosRegistroAnalisis;
import com.energiai.dto.DatosRegistroConsumo;                                                                                                                                
import com.energiai.exception.ServicioMlNoDisponibleException;                                                                                                                
                                                                                                                                                                                  
@Component                                                                                                                                                                    
public class MlClient {                                                                                                                                                       
                                                                                                                                                                                  
    private final RestClient restClient;                                                                                                                                      
    private final String mlServiceUrl;                                                                                                                                        
                                                                                                                                                                                                                                                                                        
    public MlClient(RestClient restClient, @Value("${ml.service.url:http://localhost:8000}") String mlServiceUrl) {                                                           
        this.restClient = restClient;                                                                                                                                         
        this.mlServiceUrl = mlServiceUrl;                                                                                                                                     
    }                                                                                                                                                                                                                                                                                                                                          
    public DatosRegistroAnalisis predecir(DatosRegistroConsumo datos) {                                                                                                       
        try {                                                                                                                                                                 
            return restClient.post()                                                                                                                                          
                    .uri(mlServiceUrl + "/analisis-energetico")                                                                                                                           
                    .contentType(MediaType.APPLICATION_JSON)                                                                                                                  
                    .body(datos)                                                                                                                                              
                    .retrieve()                                                                                                                                               
                    .body(DatosRegistroAnalisis.class);                                                                                                                       
        } catch (Exception e) {                                                                                                                                               
            throw new ServicioMlNoDisponibleException("El servicio Machine Learning no se encuentra disponible");                                                             
        }                                                                                                                                                                     
    }                                                                                                                                                                         
}