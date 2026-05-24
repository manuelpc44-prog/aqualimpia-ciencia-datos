# utils.py - Funciones modulares reutilizables para análisis de AquaLimpia S.A.
# Librerías: NumPy, SciPy, Joblib, Pandas

import numpy as np
import pandas as pd
from scipy import stats
from joblib import Parallel, delayed
import warnings
warnings.filterwarnings("ignore")


# --- 1. CARGA Y LIMPIEZA ------------------------------------------------------

def cargar_dataset(ruta: str) -> pd.DataFrame:
    #Carga el dataset desde un archivo Excel y parsea fechas.#
    df = pd.read_excel(ruta)
    df["fecha_registro"] = pd.to_datetime(df["fecha_registro"])
    df = df.sort_values("fecha_registro").reset_index(drop=True)
    return df


def evaluar_calidad(df: pd.DataFrame) -> dict:
# ============================================================
  # Evalúa la calidad del dataset:
  # Valores nulos
  # Duplicados
  # Outliers (IQR) en columnas numéricas
  # Rangos esperados para parámetros ambientales
# ============================================================
    numericas = df.select_dtypes(include=[np.number]).columns.tolist()
    nulos = df.isnull().sum().to_dict()
    duplicados = int(df.duplicated().sum())

    # Outliers por IQR
    outliers = {}
    for col in numericas:
        Q1, Q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        IQR = Q3 - Q1
        n_out = int(((df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)).sum())
        outliers[col] = n_out

    # Validaciones de dominio
    advertencias = []
    if (df["pH_entrada"] < 4).any() or (df["pH_entrada"] > 10).any():
        advertencias.append("pH fuera de rango operativo (4–10)")
    if (df["DBO_salida_mg_L"] < 0).any():
        advertencias.append("DBO salida con valores negativos")
    if (df["caudal_entrada_m3_d"] <= 0).any():
        advertencias.append("Caudal de entrada con valores no positivos")

    return {
        "total_registros": len(df),
        "nulos": nulos,
        "duplicados": duplicados,
        "outliers_IQR": outliers,
        "advertencias_dominio": advertencias,
    }


# --- 2. INDICADORES CLAVE -----------------------------------------------------

def calcular_eficiencia_dbo(df: pd.DataFrame) -> pd.Series:
 # ============================================================
 #  Calcula la eficiencia de remoción de DBO (%) por registro.
 # ============================================================
    return ((df["DBO_entrada_mg_L"] - df["DBO_salida_mg_L"]) / df["DBO_entrada_mg_L"] * 100).round(2)


def resumen_por_planta(df: pd.DataFrame) -> pd.DataFrame:
# ============================================================
# Genera estadísticas descriptivas agrupadas por planta.
# ============================================================
    df = df.copy()
    df["eficiencia_DBO"] = calcular_eficiencia_dbo(df)
    grp = df.groupby("planta").agg(
        registros=("fecha_registro", "count"),
        caudal_promedio=("caudal_entrada_m3_d", "mean"),
        DBO_entrada_promedio=("DBO_entrada_mg_L", "mean"),
        DBO_salida_promedio=("DBO_salida_mg_L", "mean"),
        eficiencia_DBO_media=("eficiencia_DBO", "mean"),
        energia_promedio=("energia_aeracion_kWh", "mean"),
        lodos_promedio=("lodos_generados_kg_d", "mean"),
        tasa_cumplimiento=("cumplimiento_norma", "mean"),
    ).round(2)
    return grp


# --- 3. ESTADÍSTICAS AVANZADAS (SciPy) ---------------------------------------

def prueba_normalidad(df: pd.DataFrame, columna: str) -> dict:
    #Prueba de Shapiro-Wilk para normalidad.#
    stat, p = stats.shapiro(df[columna].dropna())
    return {"columna": columna, "estadistico": round(stat, 4), "p_valor": round(p, 4),
            "normal": p > 0.05}


def correlacion_spearman(df: pd.DataFrame, col_x: str, col_y: str) -> dict:
    #Correlación de Spearman entre dos variables.#
    rho, p = stats.spearmanr(df[col_x].dropna(), df[col_y].dropna())
    return {"variable_x": col_x, "variable_y": col_y,
            "rho": round(rho, 4), "p_valor": round(p, 4)}


def estadisticas_numpy(df: pd.DataFrame, columna: str) -> dict:
    #Estadísticas descriptivas usando NumPy.#
    arr = df[columna].dropna().values
    return {
        "media": round(np.mean(arr), 2),
        "mediana": round(np.median(arr), 2),
        "desv_std": round(np.std(arr), 2),
        "varianza": round(np.var(arr), 2),
        "min": round(np.min(arr), 2),
        "max": round(np.max(arr), 2),
        "percentil_25": round(np.percentile(arr, 25), 2),
        "percentil_75": round(np.percentile(arr, 75), 2),
    }


# --- 4. PROCESAMIENTO PARALELO (Joblib) ---------------------------------------

def _estadisticas_col(df, col):
    return {col: estadisticas_numpy(df, col)}


def estadisticas_todas_columnas(df: pd.DataFrame) -> dict:
    #Calcula estadísticas NumPy de todas las columnas numéricas en paralelo (Joblib).#
    numericas = df.select_dtypes(include=[np.number]).columns.tolist()
    resultados = Parallel(n_jobs=-1)(
        delayed(_estadisticas_col)(df, col) for col in numericas
    )
    out = {}
    for r in resultados:
        out.update(r)
    return out


# --- 5. GENERACIÓN DE ARCHIVOS DE ÁREA ---------------------------------------

def generar_archivo_operaciones(df: pd.DataFrame, ruta_salida: str) -> None:
    #Genera el archivo para el Área de Operaciones.#
    cols = ["fecha_registro", "planta", "caudal_entrada_m3_d",
            "DBO_entrada_mg_L", "DBO_salida_mg_L",
            "energia_aeracion_kWh", "lodos_generados_kg_d"]
    df_op = df[cols].copy()
    df_op["eficiencia_DBO_%"] = calcular_eficiencia_dbo(df)
    df_op["alerta"] = np.where(df_op["DBO_salida_mg_L"] > 30, "ALERTA", "OK")
    df_op.to_excel(ruta_salida, index=False)


def generar_archivo_ambiental(df: pd.DataFrame, ruta_salida: str) -> None:
    #Genera el archivo para el Área de Gestión Ambiental.#
    cols = ["fecha_registro", "planta", "DBO_salida_mg_L", "cumplimiento_norma"]
    df_amb = df[cols].copy()
    df_amb["estado"] = df_amb["cumplimiento_norma"].map({1: "CUMPLE", 0: "INCUMPLE"})
    df_amb.to_excel(ruta_salida, index=False)
