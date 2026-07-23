import numpy as np
import pandas as pd


def generar_datos_base(num_clientes: int, seed: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    ids = np.arange(1, num_clientes + 1)

    df_hogar = pd.DataFrame({
        "id_cliente": ids,
        "tipo_vivienda": rng.choice(["casa", "departamento", "duplex"], size=num_clientes,
                                    p=[0.55, 0.35, 0.10]),
        "superficie_m2": np.round(rng.normal(75, 25, num_clientes).clip(30, 180), 1),
        "calefaccion": rng.choice(["gas", "electrica", "ninguna"], size=num_clientes,
                                  p=[0.45, 0.40, 0.15]),
        "region": rng.choice(["norte", "centro", "sur"], size=num_clientes,
                             p=[0.30, 0.45, 0.25]),
        "ingresos": np.round(rng.normal(1500, 600, num_clientes).clip(400, 6000), 0),
    })

    df_equipamientos = pd.DataFrame({
        "id_cliente": ids,
        "cant_electrodomesticos": rng.integers(4, 18, num_clientes),
        "anio_promedio": rng.integers(2005, 2024, num_clientes),
        "eficiencia_promedio": rng.choice(["A_plus", "A", "B", "C"],
                                          size=num_clientes, p=[0.20, 0.35, 0.30, 0.15]),
        "energia_renovable": rng.choice(["si", "no"], size=num_clientes, p=[0.25, 0.75]),
    })

    base = (
        1.6 * df_hogar["superficie_m2"]
        + 4.2 * df_equipamientos["cant_electrodomesticos"]
        + (df_hogar["calefaccion"] == "electrica").astype(int) * 110
        + (df_hogar["calefaccion"] == "gas").astype(int) * -8
        + (df_equipamientos["eficiencia_promedio"] == "C").astype(int) * 50
        + (df_equipamientos["eficiencia_promedio"] == "B").astype(int) * 12
        - (df_equipamientos["eficiencia_promedio"] == "A_plus").astype(int) * 30
        - (df_equipamientos["energia_renovable"] == "si").astype(int) * 18
        + 35
    )
    df_consumo = pd.DataFrame({
        "id_cliente": ids,
        "consumo_total_kwh": np.round(base + rng.normal(0, 28, num_clientes), 1),
    })

    return df_hogar, df_consumo, df_equipamientos
