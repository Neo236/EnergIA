import numpy as np
import pandas as pd
import pytest

from domain.scoring import (
    BINS_ANTIGUEDAD,
    BINS_CONSUMO,
    BINS_EQUIPOS,
    BINS_HORAS,
    BINS_M2,
    PESOS,
    calcular_iee,
    calcular_iee_y_categoria,
    obtener_categoria,
    score_consumo,
    score_eficiencia,
    score_equipamiento,
    score_contexto,
)


# ---------------------------------------------------------------------------
# Hogares de muestra del data_colab.ipynb (Fase 4 + Fase 6 outputs)
# ---------------------------------------------------------------------------
HOGAR_0001 = {
    "tipo_inmueble": "Departamento", "metros_cuadrados": 1269,
    "antiguedad_vivienda": 61, "zona_fria": "No", "calidad_aislamiento": "Muy Baja",
    "fuente_calefaccion": "Solar", "fuente_agua_caliente": "Electricidad",
    "consumo_kwh": 363.4, "uso_horario_pico": "Si",
    "horas_alto_consumo": 14, "cantidad_equipos": 19,
    "categoria_esperada": "Moderado",
}
HOGAR_0004 = {
    "tipo_inmueble": "Departamento", "metros_cuadrados": 2000,
    "antiguedad_vivienda": 5, "zona_fria": "Si", "calidad_aislamiento": "Muy Baja",
    "fuente_calefaccion": "Electricidad", "fuente_agua_caliente": "Solar",
    "consumo_kwh": 542.9, "uso_horario_pico": "Si",
    "horas_alto_consumo": 23, "cantidad_equipos": 85,
    "categoria_esperada": "Ineficiente",
}
HOGAR_0005 = {
    "tipo_inmueble": "Casa", "metros_cuadrados": 1269,
    "antiguedad_vivienda": 57, "zona_fria": "No", "calidad_aislamiento": "Muy Alta",
    "fuente_calefaccion": "Electricidad", "fuente_agua_caliente": "Electricidad",
    "consumo_kwh": 433.4, "uso_horario_pico": "Si",
    "horas_alto_consumo": 13, "cantidad_equipos": 90,
    "categoria_esperada": "Moderado",
}


def _df(h):
    return pd.DataFrame([{k: v for k, v in h.items() if k != "categoria_esperada"}])


class TestConstantes:
    def test_pesos_suman_uno(self):
        assert abs(sum(PESOS.values()) - 1.0) < 1e-9

    def test_bins_consumo_4_edges(self):
        assert len(BINS_CONSUMO) == 4
        assert BINS_CONSUMO[0] == pytest.approx(0.1)
        assert BINS_CONSUMO[-1] == pytest.approx(1000)

    def test_bins_antiguedad_5_edges(self):
        assert len(BINS_ANTIGUEDAD) == 5
        assert BINS_ANTIGUEDAD[0] == 0
        assert BINS_ANTIGUEDAD[-1] == 150


class TestScoreConsumo:
    def test_consumo_bajo_sin_poco_horas(self):
        df = _df({**HOGAR_0001, "consumo_kwh": 100, "uso_horario_pico": "No",
                  "horas_alto_consumo": 1})
        s = score_consumo(df).iloc[0]
        assert s == 60 + 20 + 20

    def test_consumo_alto_pico_y_muchas_horas(self):
        df = _df({**HOGAR_0001, "consumo_kwh": 900, "uso_horario_pico": "Si",
                  "horas_alto_consumo": 22})
        s = score_consumo(df).iloc[0]
        assert s == 20 + 0 + 7


class TestScoreEficiencia:
    def test_mejor_caso(self):
        df = _df({**HOGAR_0001,
                  "calidad_aislamiento": "Muy Alta",
                  "fuente_calefaccion": "Solar",
                  "fuente_agua_caliente": "Solar"})
        s = score_eficiencia(df).iloc[0]
        assert s == 40 + 30 + 30

    def test_peor_caso(self):
        df = _df({**HOGAR_0001,
                  "calidad_aislamiento": "Muy Baja",
                  "fuente_calefaccion": "Electricidad",
                  "fuente_agua_caliente": "Electricidad"})
        s = score_eficiencia(df).iloc[0]
        assert s == 8 + 5 + 5


class TestScoreEquipamiento:
    def test_pocos_equipos(self):
        df = _df({**HOGAR_0001, "cantidad_equipos": 5})
        assert score_equipamiento(df).iloc[0] == 100

    def test_muchos_equipos(self):
        df = _df({**HOGAR_0001, "cantidad_equipos": 95})
        assert score_equipamiento(df).iloc[0] == 33


class TestScoreContexto:
    def test_casa_grande_nueva_zona_fria(self):
        df = _df({**HOGAR_0001,
                  "tipo_inmueble": "Casa",
                  "metros_cuadrados": 2000,
                  "antiguedad_vivienda": 5,
                  "zona_fria": "Si"})
        s = score_contexto(df).iloc[0]
        assert s == 30 + 10 + 20 + 20

    def test_pyme_chico_viejo_no_frio(self):
        df = _df({**HOGAR_0001,
                  "tipo_inmueble": "Pyme",
                  "metros_cuadrados": 50,
                  "antiguedad_vivienda": 140,
                  "zona_fria": "No"})
        s = score_contexto(df).iloc[0]
        assert s == 5 + 30 + 5 + 0

    def test_acepta_int_para_zona_fria(self):
        """Si zona_fria llega como int 0/1 (desde simulation.py) debe funcionar."""
        df = pd.DataFrame([{
            "tipo_inmueble": "Casa", "metros_cuadrados": 1000,
            "antiguedad_vivienda": 50, "zona_fria": 1,
        }])
        assert score_contexto(df).iloc[0] == 30 + 20 + 15 + 20

    def test_acepta_bool_para_zona_fria(self):
        df = pd.DataFrame([{
            "tipo_inmueble": "Casa", "metros_cuadrados": 1000,
            "antiguedad_vivienda": 50, "zona_fria": True,
        }])
        assert score_contexto(df).iloc[0] == 30 + 20 + 15 + 20


class TestObtenerCategoria:
    @pytest.mark.parametrize("puntaje,esperado", [
        (100.0, "Eficiente"),
        (71.0, "Eficiente"),
        (70.0, "Moderado"),
        (50.0, "Moderado"),
        (49.999, "Ineficiente"),
        (-100.0, "Ineficiente"),
    ])
    def test_cortes_colab(self, puntaje, esperado):
        s = pd.Series([puntaje])
        assert obtener_categoria(s).iloc[0] == esperado


class TestIntegracionColab:
    """Casos de muestra del notebook data_colab.ipynb."""

    @pytest.mark.parametrize("hogar", [HOGAR_0001, HOGAR_0004, HOGAR_0005],
                             ids=["Hogar_0001", "Hogar_0004", "Hogar_0005"])
    def test_categoria_colab(self, hogar):
        df = _df(hogar)
        iee = calcular_iee(df).iloc[0]
        categoria = calcular_iee_y_categoria(df).iloc[0]
        assert categoria == hogar["categoria_esperada"], (
            f"IEE={iee:.2f} categoria={categoria} "
            f"esperado={hogar['categoria_esperada']}"
        )

    def test_hogar_0004_es_ineficiente_justo_bajo_50(self):
        """Hogar_0004 del colab: IEE≈49.0 (categoria Ineficiente)."""
        df = _df(HOGAR_0004)
        iee = calcular_iee(df).iloc[0]
        assert iee < 50.0
        assert calcular_iee_y_categoria(df).iloc[0] == "Ineficiente"
