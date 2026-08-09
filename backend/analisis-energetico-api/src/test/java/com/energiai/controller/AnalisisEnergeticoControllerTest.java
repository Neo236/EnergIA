package com.energiai.controller;

import java.util.List;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;
import org.springframework.http.MediaType;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.test.web.servlet.MockMvc;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;

import com.energiai.client.MlClient;
import com.energiai.dto.CategoriaConsumo;
import com.energiai.dto.DatosRegistroAnalisis;
import com.energiai.exception.DatosEntradaInvalidosException;
import com.energiai.exception.GlobalExceptionHandler;
import com.energiai.exception.MlRespuestaInvalidaException;
import com.energiai.exception.ServicioMlNoDisponibleException;
import com.energiai.service.AnalisisEnergeticoService;

class AnalisisEnergeticoControllerTest {

    private MockMvc mockMvc;
    private MlClient mlClient;

    @BeforeEach
    void setUp() {
        mlClient = mock(MlClient.class);
        AnalisisEnergeticoService service = new AnalisisEnergeticoService(mlClient);
        AnalisisEnergeticoController controller = new AnalisisEnergeticoController();
        ReflectionTestUtils.setField(controller, "analisisService", service);

        DatosRegistroAnalisis analisisMock = DatosRegistroAnalisis.builder()
                .categoria(CategoriaConsumo.EFICIENTE)
                .probabilidad(0.25)
                .costo_estimado_mensual(300.0)
                .recomendaciones(List.of("Buen consumo."))
                .build();

        when(mlClient.predecir(any())).thenReturn(analisisMock);

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

    @Test
    @DisplayName("POST /api/analisis: Rechaza petición con valor fuera del catálogo")
    void probarEndpointConCatalogoInvalido() throws Exception {
        String jsonInvalido = """
            {
              "consumo_electrico_kwh": 300.0,
              "cantidad_equipos": 5,
              "tipo_inmueble": "OPCION_INEXISTENTE",
              "uso_horario_pico": true,
              "horas_alto_consumo": 5,
              "metros_cuadrados": 50,
              "antiguedad_vivienda": 10,
              "zona_fria": false,
              "calidad_aislamiento": "MEDIA",
              "fuente_calefaccion": "SOLAR",
              "fuente_agua_caliente": "ELECTRICIDAD"
            }
            """;

        mockMvc.perform(post("/api/v1/analisis-energetico")
                .contentType(MediaType.APPLICATION_JSON)
                .content(jsonInvalido))
                .andExpect(status().isBadRequest());
    }

    @Test
    @DisplayName("POST /api/v1/analisis-energetico: Retorna 503 cuando el servicio de ML no está disponible")
    void testServicioMlNoDisponibleRetorna503() throws Exception {
        when(mlClient.predecir(any())).thenThrow(new ServicioMlNoDisponibleException("El servicio Machine Learning no se encuentra disponible"));

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
                .andExpect(status().isServiceUnavailable())
                .andExpect(jsonPath("$.status").value(503))
                .andExpect(jsonPath("$.mensaje").value("El servicio Machine Learning no se encuentra disponible"));
    }

    @Test
    @DisplayName("POST /api/v1/analisis-energetico: Retorna 400 cuando FastAPI rechaza los datos (422 → 400)")
    void testDatosEntradaInvalidosRetorna400() throws Exception {
        when(mlClient.predecir(any()))
                .thenThrow(new DatosEntradaInvalidosException("El servicio de Machine Learning rechazó los datos de entrada (HTTP 422)"));

        mockMvc.perform(post("/api/v1/analisis-energetico")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {
                      "consumo_kwh": 450.5,
                      "cantidad_equipos": 8,
                      "tipo_inmueble": "Casa",
                      "horas_alto_consumo": 6
                    }
                    """))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.status").value(400))
                .andExpect(jsonPath("$.error").value("BAD_REQUEST"));
    }

    @Test
    @DisplayName("POST /api/v1/analisis-energetico: Retorna 502 cuando FastAPI devuelve respuesta inválida")
    void testMlRespuestaInvalidaRetorna502() throws Exception {
        when(mlClient.predecir(any()))
                .thenThrow(new MlRespuestaInvalidaException("El servicio Machine Learning devolvió una respuesta inesperada o inválida"));

        mockMvc.perform(post("/api/v1/analisis-energetico")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {
                      "consumo_kwh": 450.5,
                      "cantidad_equipos": 8,
                      "tipo_inmueble": "Casa",
                      "horas_alto_consumo": 6
                    }
                    """))
                .andExpect(status().isBadGateway())
                .andExpect(jsonPath("$.status").value(502))
                .andExpect(jsonPath("$.error").value("BAD_GATEWAY"));
    }
}