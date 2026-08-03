    package com.energiai.dto;                                                                                                                                                     
                                                                                                                                                                                  
    import jakarta.validation.Validation;                                                                                                                                         
    import jakarta.validation.Validator;                                                                                                                                          
    import jakarta.validation.ValidatorFactory;                                                                                                                                   
    import org.junit.jupiter.api.BeforeEach;                                                                                                                                      
    import org.junit.jupiter.api.DisplayName;                                                                                                                                     
    import org.junit.jupiter.api.Test;                                                                                                                                            
                                                                                                                                                                                  
    import static org.junit.jupiter.api.Assertions.*;                                                                                                                             
                                                                                                                                                                                  
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
                    -50.0, // Invalido (@Positive)                                                                                                                                
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
                    null, // Invalido (@NotNull)                                                                                                                                  
                    null, null, null, null, null, null, null, null, null, null                                                                                                    
            );                                                                                                                                                                    
                                                                                                                                                                                  
            var violaciones = validator.validate(dto);                                                                                                                            
            // Debe detectar violaciones en todos los campos marcados con @NotNull                                                                                                
            assertTrue(violaciones.size() >= 11);                                                                                                                                 
        }                                                                                                                                                                         
    }