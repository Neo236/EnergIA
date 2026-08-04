import pytest

from domain.recommendations import calcular_recomendaciones


class TestCalcularRecomendaciones:
    def test_devuelve_lista_no_vacia(self):
        recs = calcular_recomendaciones({"consumo_kwh": 200})
        assert isinstance(recs, list)
        assert len(recs) >= 1

    def test_consumo_muy_alto_recomienda_revisar(self):
        recs = calcular_recomendaciones({"consumo_kwh": 800})
        assert any("elevado" in r for r in recs)

    def test_consumo_medio_alto_recomienda_auditar(self):
        recs = calcular_recomendaciones({"consumo_kwh": 500})
        assert any("encima del promedio" in r for r in recs)

    def test_aislacion_muy_baja_recomienda_mejorar(self):
        recs = calcular_recomendaciones({"calidad_aislamiento": "Muy Baja"})
        assert any("aislamiento" in r.lower() for r in recs)

    def test_aislacion_baja_recomienda_reforzar(self):
        recs = calcular_recomendaciones({"calidad_aislamiento": "Baja"})
        assert any("puertas y ventanas" in r for r in recs)

    def test_fuente_electricidad_recomienda_solar(self):
        recs = calcular_recomendaciones({"fuente_calefaccion": "Electricidad"})
        assert any("Solar" in r or "Gas" in r for r in recs)

    def test_zona_fria_recomienda_priorizar(self):
        recs = calcular_recomendaciones({"zona_fria": True})
        assert any("zona fría" in r.lower() for r in recs)

    def test_horas_altas_recomienda_centralizar(self):
        recs = calcular_recomendaciones({"horas_alto_consumo": 20})
        assert any("horarios" in r for r in recs)

    def test_muchos_equipos_recomienda_reemplazo(self):
        recs = calcular_recomendaciones({"cantidad_equipos": 80})
        assert any("A+" in r or "clase" in r for r in recs)

    def test_antiguedad_alta_recomienda_revision(self):
        recs = calcular_recomendaciones({"antiguedad_vivienda": 100})
        assert any("80 años" in r for r in recs)

    def test_caso_ideal_solo_recomendacion_neutral(self):
        recs = calcular_recomendaciones({
            "consumo_kwh": 200,
            "calidad_aislamiento": "Alta",
            "fuente_calefaccion": "Solar",
            "fuente_agua_caliente": "Solar",
            "zona_fria": False,
            "horas_alto_consumo": 5,
            "cantidad_equipos": 10,
            "antiguedad_vivienda": 10,
        })
        assert recs == ["Tu hogar está bien calibrado. Mantén hábitos de consumo eficientes."]

    def test_multiples_reglas_se_acumulan(self):
        recs = calcular_recomendaciones({
            "consumo_kwh": 800,
            "calidad_aislamiento": "Muy Baja",
            "fuente_calefaccion": "Electricidad",
            "zona_fria": True,
            "horas_alto_consumo": 20,
            "cantidad_equipos": 90,
            "antiguedad_vivienda": 120,
        })
        assert len(recs) >= 5