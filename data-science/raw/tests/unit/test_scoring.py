import numpy as np
import pytest

from domain.scoring import (
    asignar_categoria_por_score,
    calcular_score_eficiencia,
)


class TestCalcularScoreEficiencia:
    def test_score_alto_consumo_baja_aislacion_zona_fria_es_negativo(self):
        score = calcular_score_eficiencia({
            "consumo_kwh": 900,
            "calidad_aislamiento": "Muy Baja",
            "fuente_calefaccion": "Electricidad",
            "fuente_agua_caliente": "Electricidad",
            "zona_fria": True,
            "horas_alto_consumo": 24,
            "cantidad_equipos": 100,
        })
        assert score < -10

    def test_score_bajo_consumo_solar_aislacion_alta_es_positivo(self):
        score = calcular_score_eficiencia({
            "consumo_kwh": 100,
            "calidad_aislamiento": "Muy Alta",
            "fuente_calefaccion": "Solar",
            "fuente_agua_caliente": "Solar",
            "zona_fria": False,
            "horas_alto_consumo": 2,
            "cantidad_equipos": 5,
        })
        assert score > 15

    def test_score_alias_consumo_electrico_kwh(self):
        score_a = calcular_score_eficiencia({"consumo_kwh": 500})
        score_b = calcular_score_eficiencia({"consumo_electrico_kwh": 500})
        assert score_a == score_b

    def test_score_defaults_cuando_faltan_keys(self):
        score = calcular_score_eficiencia({})
        assert isinstance(score, float)


class TestAsignarCategoriaPorScore:
    def test_score_alto_es_eficiente(self):
        assert asignar_categoria_por_score(50.0, (0.0, 20.0)) == "Eficiente"

    def test_score_medio_es_moderado(self):
        assert asignar_categoria_por_score(10.0, (0.0, 20.0)) == "Moderado"

    def test_score_bajo_es_ineficiente(self):
        assert asignar_categoria_por_score(-50.0, (0.0, 20.0)) == "Ineficiente"

    def test_frontera_igual_a_cuantil_eficiente(self):
        assert asignar_categoria_por_score(20.0, (0.0, 20.0)) == "Eficiente"

    def test_frontera_igual_a_cuantil_ineficiente(self):
        assert asignar_categoria_por_score(0.0, (0.0, 20.0)) == "Moderado"

    @pytest.mark.parametrize("categoria_esperada,score,cuantiles", [
        ("Eficiente", 100.0, (-50.0, 10.0)),
        ("Eficiente", 11.0, (-50.0, 10.0)),
        ("Moderado", 9.0, (-50.0, 10.0)),
        ("Moderado", -49.0, (-50.0, 10.0)),
        ("Ineficiente", -100.0, (-50.0, 10.0)),
        ("Ineficiente", -51.0, (-50.0, 10.0)),
    ])
    def test_categorias_parametrizadas(self, categoria_esperada, score, cuantiles):
        assert asignar_categoria_por_score(score, cuantiles) == categoria_esperada