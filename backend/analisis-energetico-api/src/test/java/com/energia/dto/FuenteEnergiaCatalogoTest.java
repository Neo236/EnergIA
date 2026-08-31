    package com.energia.dto;                                                                                                                                                     
                                                                                                                                                                                  
    import static org.junit.jupiter.api.Assertions.assertNotNull;
    import static org.junit.jupiter.api.Assertions.assertNull;
    import static org.junit.jupiter.api.Assertions.assertThrows;
    import org.junit.jupiter.api.DisplayName;
    import org.junit.jupiter.api.Test;
    import org.junit.jupiter.params.ParameterizedTest;                                                                                                                             
    import org.junit.jupiter.params.provider.ValueSource;
                                                                                                                                                                                  
    class FuenteEnergiaCatalogoTest {                                                                                                                                             
                                                                                                                                                                                  
        @ParameterizedTest                                                                                                                                                        
        @ValueSource(strings = {"Solar", "SOLAR", "Electricidad", "ELECTRICIDAD", "Otros", "OTROS"})                                                                              
        @DisplayName("Catálogo FuenteEnergia: Debe aceptar todos los valores válidos del catálogo")                                                                               
        void probarValoresValidosCatalogo(String entrada) {                                                                                                                       
            FuenteEnergia fuente = FuenteEnergia.fromValue(entrada);                                                                                                              
            assertNotNull(fuente, "El catálogo debe reconocer " + entrada);                                                                                                       
        }                                                                                                                                                                         
                                                                                                                                                                                  
        @Test                                                                                                                                                                     
        @DisplayName("Catálogo FuenteEnergia: Debe rechazar valores fuera del catálogo")                                                                                          
        void probarValorInvalidoCatalogo() {                                                                                                                                      
            assertThrows(IllegalArgumentException.class, () -> {                                                                                                                  
                FuenteEnergia.fromValue("PETROLEO"); // No existe en el catálogo                                                                                                  
            });                                                                                                                                                                   
        }                                                                                                                                                                         
                                                                                                                                                                                  
        @Test                                                                                                                                                                     
        @DisplayName("Catálogo FuenteEnergia: Retorna nulo si el valor es vacío")                                                                                                 
        void probarValorVacio() {                                                                                                                                                 
            assertNull(FuenteEnergia.fromValue(""));                                                                                                                              
            assertNull(FuenteEnergia.fromValue(null));                                                                                                                            
        }                                                                                                                                                                         
    }