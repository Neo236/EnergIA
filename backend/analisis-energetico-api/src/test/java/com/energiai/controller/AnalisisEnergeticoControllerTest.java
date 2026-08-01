package com.energiai.controller;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;

import com.energiai.exception.GlobalExceptionHandler;
import com.energiai.service.AnalisisEnergeticoService;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultHandlers.print;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

class AnalisisEnergeticoControllerTest {

    private MockMvc mockMvc;

    @BeforeEach
    void setUp() {
        AnalisisEnergeticoController controller = new AnalisisEnergeticoController();
        AnalisisEnergeticoService service = new AnalisisEnergeticoService();
        org.springframework.test.util.ReflectionTestUtils.setField(controller, "analisisService", service);

        mockMvc = MockMvcBuilders.standaloneSetup(controller)
                .setControllerAdvice(new GlobalExceptionHandler())
                .build();
    }

    @Test
    void testAnalizarConsumoConCasaTitleCase() throws Exception {
        String json = """
            {
              "consumo_kwh": 450.5,
              "cantidad_equipos": 8,
              "tipo_inmueble": "Casa",
              "uso_horario_pico": true,
              "horas_alto_consumo": 6,
              "metros_cuadrados": 30,
              "antiguedad_vivienda": 34,
              "zona_fria": false,
              "calidad_aislamiento": "Media",
              "fuente_calefaccion": "Solar",
              "fuente_agua_caliente": "Electricidad"
            }
            """;

        mockMvc.perform(post("/api/v1/analisis-energetico")
                .contentType(MediaType.APPLICATION_JSON)
                .content(json))
                .andExpect(status().isOk());
    }

    @Test
    void testAnalizarConsumoConCASAUpperCase() throws Exception {
        String json = """
            {
              "consumo_kwh": 450.5,
              "cantidad_equipos": 8,
              "tipo_inmueble": "CASA",
              "uso_horario_pico": true,
              "horas_alto_consumo": 6,
              "metros_cuadrados": 30,
              "antiguedad_vivienda": 34,
              "zona_fria": false,
              "calidad_aislamiento": "MEDIA",
              "fuente_calefaccion": "SOLAR",
              "fuente_agua_caliente": "ELECTRICIDAD"
            }
            """;

        mockMvc.perform(post("/api/v1/analisis-energetico")
                .contentType(MediaType.APPLICATION_JSON)
                .content(json))
                .andExpect(status().isOk());
    }

    @Test
    void testAnalizarConsumoConCasaLowerCase() throws Exception {
        String json = """
            {
              "consumo_kwh": 450.5,
              "cantidad_equipos": 8,
              "tipo_inmueble": "casa",
              "uso_horario_pico": true,
              "horas_alto_consumo": 6,
              "metros_cuadrados": 30,
              "antiguedad_vivienda": 34,
              "zona_fria": false,
              "calidad_aislamiento": "media",
              "fuente_calefaccion": "solar",
              "fuente_agua_caliente": "electricidad"
            }
            """;

        mockMvc.perform(post("/api/v1/analisis-energetico")
                .contentType(MediaType.APPLICATION_JSON)
                .content(json))
                .andExpect(status().isOk());
    }

    @Test
    void testAnalizarConsumoConTipoInmuebleInvalido_Retorna400() throws Exception {
        String json = """
            {
              "consumo_kwh": 450.5,
              "cantidad_equipos": 8,
              "tipo_inmueble": "Invalido",
              "uso_horario_pico": true,
              "horas_alto_consumo": 6,
              "metros_cuadrados": 30,
              "antiguedad_vivienda": 34,
              "zona_fria": false,
              "calidad_aislamiento": "MEDIA",
              "fuente_calefaccion": "SOLAR",
              "fuente_agua_caliente": "ELECTRICIDAD"
            }
            """;

        mockMvc.perform(post("/api/v1/analisis-energetico")
                .contentType(MediaType.APPLICATION_JSON)
                .content(json))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.status").value(400));
    }
}
