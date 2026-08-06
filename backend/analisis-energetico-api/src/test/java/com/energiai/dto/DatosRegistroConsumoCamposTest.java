package com.energiai.dto;                                                                                                                                                     
                                                                                                                                                                                  
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import jakarta.validation.Validation;
import jakarta.validation.Validator;
import jakarta.validation.ValidatorFactory;
                                                                                                                                                                                  
class DatosRegistroConsumoCamposTest {                                                                                                                                        
                                                                                                                                                                                  
    private Validator validator;                                                                                                                                              
                                                                                                                                                                                  
    @BeforeEach                                                                                                                                                               
    void setUp() {                                                                                                                                                            
        ValidatorFactory factory = Validation.buildDefaultValidatorFactory();                                                                                                 
        validator = factory.getValidator();                                                                                                                                   
    }                                                                                                                                                                         
                                                                                                                                                                                  
    @Test                                                                                                                                                                     
    @DisplayName("Campo consumo_kwh: Debe fallar si es negativo o cero")                                                                                                      
    void probarConsumoKwhInvalido() {                                                                                                                                         
        var dto = new DatosRegistroConsumo(                                                                                                                                   
                -50.0,                                                                                                                                 
                5, TipoInmueble.CASA, true, 4, 100, 10, false,                                                                                                                
                CalidadAislamiento.MEDIA, FuenteEnergia.SOLAR, FuenteEnergia.ELECTRICIDAD                                                                                     
        );                                                                                                                                                                    
                                                                                                                                                                                  
        var violaciones = validator.validate(dto);                                                                                                                            
        assertFalse(violaciones.isEmpty(), "Debería fallar la validación por consumo_kwh negativo");                                                                          
    }                                                                                                                                                                         
                                                                                                                                                                                  
    @Test                                                                                                                                                                     
    @DisplayName("Campo horas_alto_consumo: Debe fallar si supera las 24 horas del día")                                                                                      
    void probarHorasAltoConsumoExcedido() {                                                                                                                                   
        var dto = new DatosRegistroConsumo(                                                                                                                                   
                350.0, 5, TipoInmueble.CASA, true,                                                                                                                            
                25, // Invalido (@Max(24))                                                                                                                                    
                100, 10, false,                                                                                                                                               
                CalidadAislamiento.MEDIA, FuenteEnergia.SOLAR, FuenteEnergia.ELECTRICIDAD                                                                                     
        );                                                                                                                                                                    
                                                                                                                                                                                  
        var violaciones = validator.validate(dto);                                                                                                                            
        assertFalse(violaciones.isEmpty(), "Debería fallar porque el día solo tiene 24 horas");                                                                               
    }                                                                                                                                                                         
                                                                                                                                                                                  
    @Test                                                                                                                                                                     
    @DisplayName("Campos obligatorios: Debe fallar si algún campo viene nulo")                                                                                                
    void probarCamposObligatoriosNulos() {                                                                                                                                    
        var dto = new DatosRegistroConsumo(                                                                                                                                   
                null,                                                                                                                                 
                null, null, null, null, null, null, null, null, null, null                                                                                                    
        );                                                                                                                                                                    
                                                                                                                                                                                  
        var violaciones = validator.validate(dto);                                                                                                                                                                                                                          
        assertEquals(6, violaciones.size(), "Deberia haber exactamente 6 violaciones por los campos obligatorios.");                                                                                                                                 
    }        

    @Test
    @DisplayName("Campos opcionales: Debe pasar la validaciones si los campos opcionales vienen nulos.")
    void probarCamposOpcionalesNulosEsValido(){
        var dto = new DatosRegistroConsumo(
            150.0, null, TipoInmueble.CASA, true, null, null, null, false, null, FuenteEnergia.SOLAR, FuenteEnergia.ELECTRICIDAD
        );

        var violaciones = validator.validate(dto);
        assertTrue(violaciones.isEmpty(), "La validacion debe ser exitosa cuando los campos opciones son null");
    }                                                                                                                                                                 
}