package com.energiai.client;

import static org.junit.jupiter.api.Assertions.assertThrows;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.test.web.client.MockRestServiceServer;
import org.springframework.web.client.RestClient;

import static org.springframework.test.web.client.match.MockRestRequestMatchers.method;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.requestTo;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withStatus;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withSuccess;

import com.energiai.dto.CalidadAislamiento;
import com.energiai.dto.DatosRegistroConsumo;
import com.energiai.dto.FuenteEnergia;
import com.energiai.dto.TipoInmueble;
import com.energiai.exception.DatosEntradaInvalidosException;
import com.energiai.exception.MlRespuestaInvalidaException;
import com.energiai.exception.ServicioMlNoDisponibleException;

class MlClientTest {

    private static final String ML_URL = "http://localhost:8000";
    private static final String ENDPOINT = ML_URL + "/analisis-energetico";

    private MockRestServiceServer server;
    private MlClient mlClient;

    @BeforeEach
    void setUp() {
        RestClient.Builder builder = RestClient.builder();
        server = MockRestServiceServer.bindTo(builder).build();
        mlClient = new MlClient(builder.build(), ML_URL);
    }

    private DatosRegistroConsumo datosValidos() {
        return new DatosRegistroConsumo(
                450.5,
                8,
                TipoInmueble.CASA,
                true,
                6,
                30,
                34,
                false,
                CalidadAislamiento.MEDIA,
                FuenteEnergia.SOLAR,
                FuenteEnergia.ELECTRICIDAD
        );
    }

    @Test
    @DisplayName("FastAPI 422 (validación) => DatosEntradaInvalidosException (back-end 400)")
    void fastapi422_seTraduceA400() {
        server.expect(requestTo(ENDPOINT))
                .andExpect(method(HttpMethod.POST))
                .andRespond(withStatus(HttpStatus.UNPROCESSABLE_ENTITY)
                        .contentType(MediaType.APPLICATION_JSON));

        assertThrows(DatosEntradaInvalidosException.class,
                () -> mlClient.predecir(datosValidos()));
    }

    @Test
    @DisplayName("FastAPI 503 => ServicioMlNoDisponibleException (503)")
    void fastapi503_seTraduceA503() {
        server.expect(requestTo(ENDPOINT))
                .andExpect(method(HttpMethod.POST))
                .andRespond(withStatus(HttpStatus.SERVICE_UNAVAILABLE)
                        .contentType(MediaType.APPLICATION_JSON));

        assertThrows(ServicioMlNoDisponibleException.class,
                () -> mlClient.predecir(datosValidos()));
    }

    @Test
    @DisplayName("Respuesta 200 con body inválido => MlRespuestaInvalidaException (502)")
    void bodyInvalido_seTraduceA502() {
        server.expect(requestTo(ENDPOINT))
                .andExpect(method(HttpMethod.POST))
                .andRespond(withSuccess("esto no es un json valido", MediaType.APPLICATION_JSON));

        assertThrows(MlRespuestaInvalidaException.class,
                () -> mlClient.predecir(datosValidos()));
    }

    @Test
    @DisplayName("Error de conexión (servicio caído) => ServicioMlNoDisponibleException (503)")
    void errorDeConexion_seTraduceA503() {
        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
        factory.setConnectTimeout(1000);
        factory.setReadTimeout(1000);
        RestClient clientSinMock = RestClient.builder().requestFactory(factory).build();
        MlClient clienteReal = new MlClient(clientSinMock, "http://127.0.0.1:1");

        assertThrows(ServicioMlNoDisponibleException.class,
                () -> clienteReal.predecir(datosValidos()));
    }
}
