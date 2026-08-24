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
class TestNotebookConsumeDataset:
    """Valida que la notebook Colab consume correctamente el dataset
    publicado por el pipeline Python.

    Contexto: la notebook es un CONSUMIDOR EDA, no un generador. La fuente
    de verdad de generacion y scoring IEE vive en codigo Python:
      - infrastructure/data/simulation.py  (generacion sintetica)
      - domain/scoring.py                  (reglas IEE + categoria)
      - infrastructure/config.py           (distribuciones y rangos)

    La notebook descarga `database_beta.json` desde la rama `develop`
    (publicada por el pipeline) y hace EDA / visualizacion / tests
    estadisticos (chi², ANOVA). Si el esquema del JSON cambia sin
    actualizar la notebook, este test falla.
    """

    NOTEBOOK = (
        __import__("pathlib").Path(__file__).resolve().parents[2]
        / "notebooks" / "data_colab.ipynb"
    )
    RAIZ = NOTEBOOK.parents[1]

    def _ejecutar_notebook(self, tmp) -> __import__("pathlib").Path:
        """Ejecuta la notebook via jupyter nbconvert y devuelve el path al
        .ipynb ejecutado (con outputs del kernel)."""
        import json as _json
        import os
        import shutil
        import subprocess

        assert self.NOTEBOOK.exists(), (
            f"Notebook no encontrado: {self.NOTEBOOK}. "
            "Ejecuta: python scripts/sync_colab_notebook.py --apply"
        )

        tmp_p = __import__("pathlib").Path(tmp)
        nb_copy = tmp_p / "data_colab.ipynb"
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
        executed = tmp_p / "executed.ipynb"
        return _json.loads(executed.read_bytes()), executed

    def test_notebook_ejecuta_sin_error(self, tmp_path):
        """Todas las celdas de codigo ejecutan sin excepciones."""
        nb, _ = self._ejecutar_notebook(str(tmp_path))
        errors = []
        for i, cell in enumerate(nb["cells"]):
            if cell.get("cell_type") != "code":
                continue
            for out in cell.get("outputs", []):
                if out.get("output_type") == "error":
                    errors.append((i, out.get("ename"), out.get("evalue")))
        assert not errors, (
            "La notebook tuvo errores de ejecucion:\n"
            + "\n".join(f"  cell[{i}] {n}: {e}" for i, n, e in errors)
        )

    def _stream_text(self, cell):
        """Concatena los outputs stream de una celda en un string.
        Jupyter entrega `text` como lista de lineas o como string; normalizamos."""
        chunks = []
        for o in cell.get("outputs", []):
            if o.get("output_type") != "stream":
                continue
            text = o.get("text", "")
            if isinstance(text, list):
                chunks.extend(text)
            else:
                chunks.append(text)
        return "".join(chunks)

    def test_dataset_se_descargo_y_proceso(self, tmp_path):
        """La celda df_energIA.info() reporta 2000 entradas (size del
        dataset publicado). Esto confirma que requests.get + pd.json_normalize
        funcionaron y que el dataset tiene el tamano esperado."""
        nb, _ = self._ejecutar_notebook(str(tmp_path))
        # cell [8] del notebook es `df_energIA.info()`.
        text = self._stream_text(nb["cells"][8])
        assert "2000" in text, (
            "df_energIA.info() no reporta 2000 entries. "
            "Posible causa: la URL del dataset no resuelve o el schema "
            "cambio sin actualizar la notebook.\n"
            f"Output capturado: {text[:400]}"
        )

    def test_df_general_consolida_chi_y_anova(self, tmp_path):
        """La ultima celda (df_general) consolida chi² + ANOVA con p_valor
        para todas las variables."""
        nb, _ = self._ejecutar_notebook(str(tmp_path))
        # cell [75] del notebook es `print(df_general)`.
        text = self._stream_text(nb["cells"][75])
        assert text.strip(), "df_general no produjo output."
        assert "p_valor" in text, (
            "df_general no contiene la columna p_valor. "
            "La consolidacion chi²+ANOVA fallo."
        )
        # Esperamos al menos 11 variables (6 cat/bool + 5 num).
        variables_presentes = sum(
            1 for v in [
                "tipo_inmueble", "calidad_aislamiento", "fuente_calefaccion",
                "fuente_agua_caliente", "zona_fria", "uso_horario_pico",
                "metros_cuadrados", "antiguedad_vivienda", "consumo_kwh",
                "horas_alto_consumo", "cantidad_equipos",
            ] if v in text
        )
        assert variables_presentes >= 10, (
            f"Solo {variables_presentes}/11 variables aparecen en df_general. "
            "Esperaba ver todas las features del schema."
        )

    def test_notebook_referencia_las_11_features(self, tmp_path=None):
        """Estatico (no ejecuta la notebook): valida que las 11 features
        producidas por simulation.py estan REFERENCIADAS en el codigo de
        la notebook. Esto detecta drift entre el contrato Python y la
        notebook sin pagar el costo de ejecutar jupyter."""
        assert self.NOTEBOOK.exists(), (
            f"Notebook no encontrado: {self.NOTEBOOK}"
        )
        nb_raw = __import__("json").loads(self.NOTEBOOK.read_bytes())
        sys = __import__("sys")
        sys.path.insert(0, str(self.RAIZ))
        from scripts.sync_colab_notebook import _extract_code_cells
        code = _extract_code_cells(self.NOTEBOOK.read_bytes())

        expected_features = [
            "tipo_inmueble", "metros_cuadrados", "antiguedad_vivienda",
            "zona_fria", "calidad_aislamiento", "fuente_calefaccion",
            "fuente_agua_caliente", "consumo_kwh", "uso_horario_pico",
            "horas_alto_consumo", "cantidad_equipos",
        ]
        missing = [c for c in expected_features if c not in code]
        assert not missing, (
            f"La notebook NO referencia estas columnas de "
            f"simulation.py: {missing}. Si renombraste columnas en el "
            "contrato Python, actualiza la notebook (o viceversa)."
        )


class TestSchemaContractWithNotebook:
    """Contrato ESTATICO: el dataset local que la notebook consume debe
    coincidir con el schema que simulation.py produce.

    Garantiza que si alguien cambia el contrato (renombra columna, cambia
    dtype, agrega feature), se detecta sin necesidad de ejecutar la
    notebook Colab.
    """
    DATASET_PATH = (
        __import__("pathlib").Path(__file__).resolve().parents[3]
        / "data" / "database_beta.json"
    )

    def test_dataset_local_tiene_columnas_esperadas(self):
        import json
        import pandas as pd

        if not self.DATASET_PATH.exists():
            pytest.skip(
                f"Dataset no encontrado: {self.DATASET_PATH}. "
                "Ejecuta `make pipeline` para regenerarlo."
            )
        df = pd.read_json(self.DATASET_PATH)
        expected = {
            "hogar_id", "tipo_inmueble", "metros_cuadrados",
            "antiguedad_vivienda", "zona_fria", "calidad_aislamiento",
            "fuente_calefaccion", "fuente_agua_caliente", "consumo_kwh",
            "uso_horario_pico", "horas_alto_consumo", "cantidad_equipos",
            "categoria",
        }
        missing = expected - set(df.columns)
        extra = set(df.columns) - expected
        assert not missing, f"Columnas faltantes en dataset local: {missing}"
        assert not extra, (
            f"Columnas extra en dataset local (no esperadas por la "
            f"notebook): {extra}"
        )

    def test_dataset_local_tipos_compatibles_con_notebook(self):
        """El notebook hace `.map({"Si": True, "No": False})` sobre
        zona_fria y uso_horario_pico, asi que el JSON debe tenerlas
        como string 'Si'/'No' (no bool). Las demas categoricas deben
        ser string, las numericas deben ser int/float."""
        import json
        import pandas as pd

        if not self.DATASET_PATH.exists():
            pytest.skip(
                f"Dataset no encontrado: {self.DATASET_PATH}"
            )
        df = pd.read_json(self.DATASET_PATH)

        for col in ["zona_fria", "uso_horario_pico"]:
            assert df[col].dtype.kind in ("O", "U", "S"), (
                f"{col} deberia ser string 'Si'/'No' (la notebook hace "
                f".map({{'Si': True, 'No': False}})). dtype={df[col].dtype}"
            )
            assert set(df[col].unique()).issubset({"Si", "No"}), (
                f"{col} tiene valores fuera de {{'Si', 'No'}}: "
                f"{set(df[col].unique())}"
            )

        for col in ["tipo_inmueble", "calidad_aislamiento",
                    "fuente_calefaccion", "fuente_agua_caliente",
                    "categoria", "hogar_id"]:
            assert df[col].dtype.kind in ("O", "U", "S"), (
                f"{col} deberia ser string. dtype={df[col].dtype}"
            )

        for col in ["metros_cuadrados", "antiguedad_vivienda",
                    "horas_alto_consumo", "cantidad_equipos"]:
            assert df[col].dtype.kind == "i", (
                f"{col} deberia ser int. dtype={df[col].dtype}"
            )

        assert df["consumo_kwh"].dtype.kind == "f", (
            f"consumo_kwh deberia ser float. dtype={df['consumo_kwh'].dtype}"
        )

    def test_dataset_local_categoria_valida(self):
        import json
        import pandas as pd

        if not self.DATASET_PATH.exists():
            pytest.skip(f"Dataset no encontrado: {self.DATASET_PATH}")
        df = pd.read_json(self.DATASET_PATH)
        cats = set(df["categoria"].unique())
        assert cats == {"Eficiente", "Moderado", "Ineficiente"}, (
            f"categoria tiene valores fuera del contrato: {cats}"
        )
