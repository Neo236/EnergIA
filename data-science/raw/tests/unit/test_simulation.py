import pandas as pd
import pytest

from infrastructure.data.simulation import (
    CALIDAD_AISLAMIENTO,
    FUENTE,
    TIPO_INMUEBLE,
    generar_dataset,
)


class TestGenerarDataset:
    def test_shape_correcto(self):
        df = generar_dataset(num_clientes=500, seed=42)
        assert isinstance(df, pd.DataFrame)
        assert df.shape == (500, 13)

    def test_columnas_esperadas(self):
        df = generar_dataset(num_clientes=100, seed=42)
        expected = {
            "hogar_id", "tipo_inmueble", "metros_cuadrados", "antiguedad_vivienda",
            "zona_fria", "calidad_aislamiento", "fuente_calefaccion",
            "fuente_agua_caliente", "consumo_kwh", "uso_horario_pico",
            "horas_alto_consumo", "cantidad_equipos", "categoria",
        }
        assert set(df.columns) == expected

    def test_hogar_id_unico_y_formato(self):
        df = generar_dataset(num_clientes=100, seed=42)
        assert df["hogar_id"].is_unique
        assert df["hogar_id"].iloc[0] == "Hogar_0001"
        assert df["hogar_id"].iloc[-1] == "Hogar_0100"

    def test_tipo_inmueble_valores_permitidos(self):
        df = generar_dataset(num_clientes=500, seed=42)
        assert set(df["tipo_inmueble"].unique()).issubset(set(TIPO_INMUEBLE))

    def test_aislamiento_valores_permitidos(self):
        df = generar_dataset(num_clientes=500, seed=42)
        assert set(df["calidad_aislamiento"].unique()).issubset(set(CALIDAD_AISLAMIENTO))

    def test_fuentes_valores_permitidos(self):
        df = generar_dataset(num_clientes=500, seed=42)
        assert set(df["fuente_calefaccion"].unique()).issubset(set(FUENTE))
        assert set(df["fuente_agua_caliente"].unique()).issubset(set(FUENTE))

    def test_categorias_exactas(self):
        df = generar_dataset(num_clientes=2000, seed=42)
        assert set(df["categoria"].unique()) == {"Eficiente", "Moderado", "Ineficiente"}

    def test_distribucion_categoria_aproximada(self):
        df = generar_dataset(num_clientes=2000, seed=42)
        dist = df["categoria"].value_counts(normalize=True)
        assert 0.10 < dist["Eficiente"] < 0.25
        assert 0.55 < dist["Moderado"] < 0.70
        assert 0.10 < dist["Ineficiente"] < 0.25

    def test_rangos_numericos(self):
        df = generar_dataset(num_clientes=1000, seed=42)
        assert df["metros_cuadrados"].between(26, 2000).all()
        assert df["antiguedad_vivienda"].between(0, 150).all()
        assert df["consumo_kwh"].between(0.2, 999.9).all()
        assert df["horas_alto_consumo"].between(0, 24).all()
        assert df["cantidad_equipos"].between(1, 100).all()

    def test_reproducibilidad_mismo_seed(self):
        df_a = generar_dataset(num_clientes=200, seed=123)
        df_b = generar_dataset(num_clientes=200, seed=123)
        pd.testing.assert_frame_equal(df_a, df_b)

    def test_distinto_seed_diferentes_datos(self):
        df_a = generar_dataset(num_clientes=200, seed=1)
        df_b = generar_dataset(num_clientes=200, seed=2)
        # hogar_id es determinístico (secuencial), pero las features aleatorias deben variar
        assert df_a["hogar_id"].equals(df_b["hogar_id"])
        assert not df_a["consumo_kwh"].equals(df_b["consumo_kwh"])
        assert not df_a["tipo_inmueble"].equals(df_b["tipo_inmueble"])

    @pytest.mark.parametrize("n", [50, 100, 1000, 2000])
    def test_varias_escalas(self, n):
        df = generar_dataset(num_clientes=n, seed=42)
        assert df.shape == (n, 13)
        assert df["hogar_id"].nunique() == n