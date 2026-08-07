import pandas as pd
import pytest

from infrastructure.config import Config
from infrastructure.data.simulation import generar_dataset


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
        assert set(df["tipo_inmueble"].unique()).issubset(set(Config.TIPO_INMUEBLE))

    def test_aislamiento_valores_permitidos(self):
        df = generar_dataset(num_clientes=500, seed=42)
        assert set(df["calidad_aislamiento"].unique()).issubset(
            set(Config.CALIDAD_AISLAMIENTO)
        )

    def test_fuentes_valores_permitidos(self):
        df = generar_dataset(num_clientes=500, seed=42)
        assert set(df["fuente_calefaccion"].unique()).issubset(set(Config.FUENTE))
        assert set(df["fuente_agua_caliente"].unique()).issubset(set(Config.FUENTE))

    def test_zona_fria_y_pico_son_string(self):
        """zona_fria y uso_horario_pico llegan como 'Si'/'No' (paridad con colab)."""
        df = generar_dataset(num_clientes=200, seed=42)
        assert df["zona_fria"].dtype.kind in ("O", "U", "S")
        assert df["uso_horario_pico"].dtype.kind in ("O", "U", "S")
        assert set(df["zona_fria"].unique()).issubset({"Si", "No"})
        assert set(df["uso_horario_pico"].unique()).issubset({"Si", "No"})

    def test_categorias_exactas(self):
        df = generar_dataset(num_clientes=2000, seed=42)
        assert set(df["categoria"].unique()) == {"Eficiente", "Moderado", "Ineficiente"}

    def test_distribucion_categoria_aproximada(self):
        """Cortes IEE del colab: >70 Eficiente, 50-70 Moderado, <50 Ineficiente.
        Rangos amplios para tolerar variabilidad del RNG."""
        df = generar_dataset(num_clientes=2000, seed=42)
        dist = df["categoria"].value_counts(normalize=True)
        assert 0.10 < dist["Eficiente"] < 0.30
        assert 0.50 < dist["Moderado"] < 0.80
        assert 0.05 < dist["Ineficiente"] < 0.25

    def test_rangos_numericos(self):
        df = generar_dataset(num_clientes=1000, seed=42)
        assert df["metros_cuadrados"].between(Config.MIN_M2, Config.MAX_M2).all()
        assert df["antiguedad_vivienda"].between(Config.MIN_ANTIGUEDAD, Config.MAX_ANTIGUEDAD).all()
        assert df["consumo_kwh"].between(Config.CONSUMO_KWH_INF, Config.CONSUMO_KWH_SUP).all()
        assert df["horas_alto_consumo"].between(Config.MIN_CANTIDAD_HORAS, Config.MAX_CANTIDAD_HORAS).all()
        assert df["cantidad_equipos"].between(Config.CANTIDAD_EQUIPOS_INF, Config.CANTIDAD_EQUIPOS_SUP).all()

    def test_reproducibilidad_mismo_seed(self):
        df_a = generar_dataset(num_clientes=200, seed=123)
        df_b = generar_dataset(num_clientes=200, seed=123)
        pd.testing.assert_frame_equal(df_a, df_b)

    def test_distinto_seed_diferentes_datos(self):
        df_a = generar_dataset(num_clientes=200, seed=1)
        df_b = generar_dataset(num_clientes=200, seed=2)
        assert df_a["hogar_id"].equals(df_b["hogar_id"])
        assert not df_a["consumo_kwh"].equals(df_b["consumo_kwh"])
        assert not df_a["tipo_inmueble"].equals(df_b["tipo_inmueble"])

    @pytest.mark.parametrize("n", [50, 100, 1000, 2000])
    def test_varias_escalas(self, n):
        df = generar_dataset(num_clientes=n, seed=42)
        assert df.shape == (n, 13)
        assert df["hogar_id"].nunique() == n

    def test_sin_nulos(self):
        df = generar_dataset(num_clientes=500, seed=42)
        assert not df.isnull().any().any()


@pytest.mark.skipif(
    not __import__("shutil").which("jupyter"),
    reason=(
        "jupyter no instalado. Para correr este test:\n"
        "  1) Local: pip install jupyter nbconvert ipykernel\n"
        "  2) Docker: ./scripts/run_tests_in_docker.sh\n"
        "Antes, sincroniza el notebook con: "
        "python scripts/sync_colab_notebook.py --apply"
    )
)
class TestParidadConColabEst:
    """Paridad ESTADISTICA entre colab y simulation.py.

    Por que NO byte-a-byte: el algoritmo legacy de NumPy
    (np.random.seed + np.random.choice/randint/uniform) cambio
    entre NumPy 1.x (que uso el colab originalmente) y NumPy 2.0
    (NEP 19), y el cambio es irreversible desde codigo de usuario.
    Incluso fijando numpy<2 (1.19.5) los valores exactos difieren
    del output del colab, lo que indica que se uso una version aun
    mas antigua. Sin metadata del entorno del colab, no es posible
    replicar bit-a-bit.

    Solucion adoptada: validar paridad FUNCIONAL con tolerancias:
      - Mismo schema (columnas + tipos).
      - Rangos numericos solapados >= 80%.
      - Distribuciones de categoricas equivalentes (tol 3%).
      - Distribucion de IEE equivalente (tol 5%).
    Esto detecta drift real (cambio de probabilidades, formulas,
    logica del IEE) que es lo que importa.

    Si en el futuro se necesita paridad byte-a-byte, la opcion es
    tomar el `energy_consumption.json` ya ejecutado del colab como
    fixture y comparar contra ese snapshot, no contra una
    regeneracion.
    """

    NOTEBOOK = (
        __import__("pathlib").Path(__file__).resolve().parents[2]
        / "notebooks" / "data_colab.ipynb"
    )
    RAIZ = NOTEBOOK.parents[1]
    COLAB_OUTPUT = "energy_consumption.json"

    def _ejecutar_colab(self, tmp):
        import os
        import shutil
        import subprocess

        assert self.NOTEBOOK.exists(), (
            f"Notebook no encontrado: {self.NOTEBOOK}. "
            "Ejecuta: python scripts/sync_colab_notebook.py --apply"
        )

        nb_copy = __import__("pathlib").Path(tmp) / "data_colab.ipynb"
        shutil.copy(self.NOTEBOOK, nb_copy)

        env = os.environ.copy()
        env["PYTHONPATH"] = str(self.RAIZ)
        subprocess.run(
            [
                "jupyter", "nbconvert",
                "--to", "notebook",
                "--execute",
                "--output", "executed.ipynb",
                str(nb_copy),
            ],
            cwd=tmp, env=env,
            check=True, capture_output=True, text=True, timeout=300,
        )
        return __import__("pathlib").Path(tmp) / self.COLAB_OUTPUT

    @staticmethod
    def _distribucion(series):
        return series.value_counts(normalize=True).sort_index().to_dict()

    def test_esquema_columnas_coincide(self, tmp_path):
        import pandas as pd

        colab_json = self._ejecutar_colab(str(tmp_path))
        assert colab_json.exists()
        df_colab = pd.read_json(colab_json)

        df_py = generar_dataset(num_clientes=2000, seed=42)

        assert list(df_colab.columns) == list(df_py.columns)

    def test_rangos_numericos_coinciden(self, tmp_path):
        import pandas as pd

        colab_json = self._ejecutar_colab(str(tmp_path))
        df_colab = pd.read_json(colab_json)
        df_py = generar_dataset(num_clientes=2000, seed=42)

        for col in ["metros_cuadrados", "antiguedad_vivienda",
                    "consumo_kwh", "horas_alto_consumo", "cantidad_equipos"]:
            lo = max(df_colab[col].min(), df_py[col].min())
            hi = min(df_colab[col].max(), df_py[col].max())
            rango_colab = df_colab[col].max() - df_colab[col].min()
            assert rango_colab > 0
            overlap = (hi - lo) / rango_colab
            assert overlap >= 0.80, (
                f"Columna {col}: rangos no se superponen suficientemente "
                f"(overlap={overlap:.2%})"
            )

    @pytest.mark.parametrize("col", [
        "tipo_inmueble",
        "calidad_aislamiento",
        "fuente_calefaccion",
        "fuente_agua_caliente",
    ])
    def test_distribucion_categoricas(self, tmp_path, col):
        import pandas as pd

        colab_json = self._ejecutar_colab(str(tmp_path))
        df_colab = pd.read_json(colab_json)
        df_py = generar_dataset(num_clientes=2000, seed=42)

        dist_colab = self._distribucion(df_colab[col])
        dist_py = self._distribucion(df_py[col])

        assert set(dist_colab.keys()) == set(dist_py.keys())
        for cat in dist_colab:
            diff = abs(dist_colab[cat] - dist_py[cat])
            assert diff <= 0.03, (
                f"Distribucion {col} difiere para {cat!r}: "
                f"colab={dist_colab[cat]:.3f} py={dist_py[cat]:.3f}"
            )

    def test_distribucion_categorias_finales(self, tmp_path):
        import pandas as pd

        colab_json = self._ejecutar_colab(str(tmp_path))
        df_colab = pd.read_json(colab_json)
        df_py = generar_dataset(num_clientes=2000, seed=42)

        cats_colab = set(df_colab["categoria"].unique())
        cats_py = set(df_py["categoria"].unique())
        assert cats_colab == {"Eficiente", "Moderado", "Ineficiente"}
        assert cats_py == {"Eficiente", "Moderado", "Ineficiente"}

        dist_colab = self._distribucion(df_colab["categoria"])
        dist_py = self._distribucion(df_py["categoria"])

        for cat in dist_colab:
            diff = abs(dist_colab[cat] - dist_py[cat])
            assert diff <= 0.05, (
                f"Categoria {cat!r}: colab={dist_colab[cat]:.3f} "
                f"py={dist_py[cat]:.3f}"
            )

    def test_tipos_columnas_coinciden(self, tmp_path):
        import pandas as pd

        colab_json = self._ejecutar_colab(str(tmp_path))
        df_colab = pd.read_json(colab_json)
        df_py = generar_dataset(num_clientes=2000, seed=42)

        assert df_colab["hogar_id"].dtype.kind in ("O", "U", "S")
        for col in ["metros_cuadrados", "antiguedad_vivienda",
                    "horas_alto_consumo", "cantidad_equipos"]:
            assert df_colab[col].dtype.kind == "i"
            assert df_py[col].dtype.kind == "i"
        assert df_py["consumo_kwh"].dtype.kind == "f"
        for col in ["tipo_inmueble", "calidad_aislamiento",
                    "fuente_calefaccion", "fuente_agua_caliente",
                    "zona_fria", "uso_horario_pico"]:
            assert df_colab[col].dtype.kind in ("O", "U", "S")
