package com.energiai.service;                                                                                                                                                 
                                                                                                                                                                                  
import org.springframework.stereotype.Service;

import com.energiai.client.MlClient;
import com.energiai.dto.DatosRegistroAnalisis;
import com.energiai.dto.DatosRegistroConsumo;                                                                                                                                 
import com.energiai.exception.ServicioMlNoDisponibleException;
                                                                                                                                                                                  
@Service                                                                                                                                                                      
public class AnalisisEnergeticoService {                                                                                                                                      
                                                                                                                                                                                  
    private final MlClient mlClient;                                                                                                                                                                                                                                                                                                                                                                                                                                                               
                                                                                                                                                                                  
    public AnalisisEnergeticoService(MlClient mlClient) {                                                                                                                 
        this.mlClient = mlClient;                                                                                                                                         
    }                                                                                                                                                                         
                                                                                                                                                                                  
    public DatosRegistroAnalisis realizarAnalisis(DatosRegistroConsumo datos) {                                                                                               
        if (mlClient == null) {                                                                                                                                             
            throw new ServicioMlNoDisponibleException("El servicio Machine Learning no se encuentra disponible");
        }                                                                                                                                                                     
        return mlClient.predecir(datos);                                                                                                                                      
    }                                                                                                                                                                         
}