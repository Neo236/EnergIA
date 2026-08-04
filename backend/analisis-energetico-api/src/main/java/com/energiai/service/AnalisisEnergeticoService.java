package com.energiai.service;                                                                                                                                                 
                                                                                                                                                                                  
import java.util.List;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

import com.energiai.dto.CategoriaConsumo;
import com.energiai.dto.DatosRegistroAnalisis;                                                                                                                                
import com.energiai.dto.DatosRegistroConsumo;                                                                                                                                 
                                                                                                                                                                                  
@Service                                                                                                                                                                      
public class AnalisisEnergeticoService {                                                                                                                                      
                                                                                                                                                                                  
    private final RestClient restClient;                                                                                                                                      
                                                                                                                                                                                  
    @Value("${ml.service.url:http://localhost:5000/predict}")                                                                                                                 
    private String mlServiceUrl;                                                                                                                                              
                                                                                                                                                                                  
    public AnalisisEnergeticoService() {                                                                                                                                      
        this.restClient = null;                                                                                                                                               
    }                                                                                                                                                                         
                                                                                                                                                                                  
    public AnalisisEnergeticoService(RestClient restClient) {                                                                                                                 
        this.restClient = restClient;                                                                                                                                         
    }                                                                                                                                                                         
                                                                                                                                                                                  
    public DatosRegistroAnalisis realizarAnalisis(DatosRegistroConsumo datos) {                                                                                               
        if (restClient != null) {                                                                                                                                             
            try {                                                                                                                                                             
                DatosRegistroAnalisis respuestaMl = restClient.post()                                                                                                         
                        .uri(mlServiceUrl)                                                                                                                                    
                        .contentType(MediaType.APPLICATION_JSON)                                                                                                              
                        .body(datos)                                                                                                                                          
                        .retrieve()                                                                                                                                           
                        .body(DatosRegistroAnalisis.class);                                                                                                                   
                                                                                                                                                                                  
                if (respuestaMl != null) {                                                                                                                                    
                    return respuestaMl;                                                                                                                                       
                }                                                                                                                                                             
            } catch (Exception e) {                                                                                                                                           
                System.err.println("Servicio ML no disponible. Ejecutando análisis provisional de respaldo: " + e.getMessage());                                              
            }                                                                                                                                                                 
        }                                                                                                                                                                     
                                                                                                                                                                                  
        return realizarAnalisisProvisional(datos);                                                                                                                  
    }                                                                                                                                                                         
                                                                                                                                                                                  
    private DatosRegistroAnalisis realizarAnalisisProvisional(DatosRegistroConsumo datos) {                                                                                   
        CategoriaConsumo categoria;                                                                                                                                           
        Double probabilidad;                                                                                                                                                  
        List<String> recomendaciones;                                                                                                                                         
                                                                                                                                                                                  
        double precio = 0.75;                                                                                                                                                 
        double costoEstimado = Math.round((datos.consumo_kwh() * precio) * 100.0) / 100.0;                                                                                    
                                                                                                                                                                                  
        if (datos.consumo_kwh() > 500 || datos.horas_alto_consumo() > 6) {                                                                                                    
            categoria = CategoriaConsumo.INEFICIENTE;                                                                                                                         
            probabilidad = 0.90;                                                                                                                                              
            recomendaciones = List.of(                                                                                                                                        
                "Consumo elevado detectado.",                                                                                                                                 
                "Se recomienda apagar equipos de alto consumo durante el horario pico.",                                                                                      
                "Revisar facturas por posibles tarifas fuera de hora.",                                                                                                       
                "Evaluar la eficiencia energética de los equipos actuales."                                                                                                   
            );

        } else if (datos.consumo_kwh() > 200) {                                                                                                                               
            categoria = CategoriaConsumo.MODERADO;                                                                                                                            
            probabilidad = 0.65;                                                                                                                                              
            recomendaciones = List.of(                                                                                                                                        
                "Consumo moderado.",                                                                                                                                          
                "Optimizar el uso de aire acondicionado.",                                                                                                                    
                "Desconectar equipos en modo Stand-by.",                                                                                                                      
                "Considerar iluminación LED."                                                                                                                                 
            );

        } else {                                                                                                                                                              
            categoria = CategoriaConsumo.EFICIENTE;                                                                                                                           
            probabilidad = 0.25;                                                                                                                                              
            recomendaciones = List.of(                                                                                                                                        
                "Excelente nivel de consumo.",                                                                                                                                
                "Mantener los hábitos actuales de ahorro.",                                                                                                                   
                "Continuar monitoreando el consumo mensual."                                                                                                                  
            );                                                                                                                                                                
        }                                                                                                                                                                     
                                                                                                                                                                              
        return DatosRegistroAnalisis.builder()                                                                                                                                
                .categoria(categoria)                                                                                                                                         
                .probabilidad(probabilidad)                                                                                                                                   
                .costo_estimado_mensual(costoEstimado)                                                                                                                        
                .recomendaciones(recomendaciones)                                                                                                                             
                .build();                                                                                                                                                     
    }                                                                                                                                                                         
}