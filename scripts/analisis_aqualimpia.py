#analisis_aqualimpia.py - Script principal de análisis de datos AquaLimpia S.A.
#Semana 8 - Ciencia de Datos IACC


import sys
import os
sys.path.insert(0, os.getcwd())

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from scipy import stats

from utils import (
    cargar_dataset, evaluar_calidad, calcular_eficiencia_dbo,
    resumen_por_planta, prueba_normalidad, correlacion_spearman,
    estadisticas_numpy, estadisticas_todas_columnas,
    generar_archivo_operaciones, generar_archivo_ambiental
)

# -- Rutas ----------------------------------------------------------------------
BASE = os.getcwd()
DATOS = os.path.join(BASE, "dataset_set_A_aguas_residuales.xlsx")
OUTPUTS = os.path.join(BASE, "outputs")
DASHBOARD = os.path.join(BASE, "dashboard")
os.makedirs(OUTPUTS, exist_ok=True)
os.makedirs(DASHBOARD, exist_ok=True)

# Paleta corporativa
COLORES = {"Planta Norte": "#1A6B9A", "Planta Centro": "#27A87A", "Planta Sur": "#E07B39"}
sns.set_theme(style="whitegrid", font_scale=1.1)

# ==================================================================================
# 1. CARGA Y CALIDAD
# ==================================================================================
print("=" * 60)
print("PROYECTO AQUALIMPIA S.A. - ANÁLISIS DE DATOS")
print("=" * 60)

df = cargar_dataset(DATOS)
df["eficiencia_DBO"] = calcular_eficiencia_dbo(df)
print(f"\n✓ Dataset cargado: {df.shape[0]} registros × {df.shape[1]} columnas")

calidad = evaluar_calidad(df)
print(f"\n[CALIDAD DE DATOS]")
print(f"  Registros totales : {calidad['total_registros']}")
print(f"  Valores nulos     : {sum(calidad['nulos'].values())}")
print(f"  Duplicados        : {calidad['duplicados']}")
print(f"  Outliers (IQR)    : {calidad['outliers_IQR']}")
if calidad["advertencias_dominio"]:
    print(f"  Advertencias      : {calidad['advertencias_dominio']}")
else:
    print("  Sin advertencias de dominio")

# ==================================================================================
# 2. ESTADÍSTICAS DESCRIPTIVAS (NumPy + Pandas)
# ==================================================================================
print("\n[ESTADÍSTICAS DESCRIPTIVAS - DBO SALIDA]")
est_dbo = estadisticas_numpy(df, "DBO_salida_mg_L")
for k, v in est_dbo.items():
    print(f"  {k:20s}: {v}")

print("\n[RESUMEN POR PLANTA]")
resumen = resumen_por_planta(df)
print(resumen.to_string())

# ==================================================================================
# 3. ANÁLISIS ESTADÍSTICO (SciPy)
# ==================================================================================
print("\n[PRUEBA DE NORMALIDAD - DBO SALIDA]")
norm = prueba_normalidad(df, "DBO_salida_mg_L")
print(f"  Shapiro-Wilk: W={norm['estadistico']}, p={norm['p_valor']}, Normal={norm['normal']}")

print("\n[CORRELACIÓN SPEARMAN - CAUDAL vs DBO SALIDA]")
corr = correlacion_spearman(df, "caudal_entrada_m3_d", "DBO_salida_mg_L")
print(f"  ρ = {corr['rho']}, p = {corr['p_valor']}")

print("\n[CORRELACIÓN SPEARMAN - DBO ENTRADA vs EFICIENCIA]")
corr2 = correlacion_spearman(df, "DBO_entrada_mg_L", "eficiencia_DBO")
print(f"  ρ = {corr2['rho']}, p = {corr2['p_valor']}")

# Estadísticas paralelas (Joblib)
print("\n[ESTADÍSTICAS PARALELAS - todas las columnas numéricas]")
todas = estadisticas_todas_columnas(df)
for col, stat in todas.items():
    print(f"  {col}: media={stat['media']}, σ={stat['desv_std']}")

# ==================================================================================
# 4. ARCHIVOS DE ÁREA
# ==================================================================================
generar_archivo_operaciones(df, os.path.join(OUTPUTS, "area_operaciones.xlsx"))
generar_archivo_ambiental(df, os.path.join(OUTPUTS, "area_gestion_ambiental.xlsx"))
print(f"\n✓ Archivos de área generados en: {OUTPUTS}")

# ==================================================================================
# 5. DASHBOARD - 6 GRÁFICOS
# ==================================================================================
fig, axes = plt.subplots(3, 2, figsize=(16, 18))
fig.suptitle("Dashboard AquaLimpia S.A. - Análisis de Aguas Residuales\nTrimestre Jul-Oct 2025",
             fontsize=16, fontweight="bold", y=0.98)

# -- G1: Tasa de cumplimiento por planta -------------------------------------
ax = axes[0, 0]
tasa = resumen["tasa_cumplimiento"] * 100
bars = ax.bar(tasa.index, tasa.values,
              color=[COLORES[p] for p in tasa.index], edgecolor="white", linewidth=1.5)
ax.axhline(30, color="red", linestyle="--", linewidth=1.5, label="Meta mínima 30%")
ax.set_title("Tasa de Cumplimiento Normativo por Planta (%)", fontweight="bold")
ax.set_ylabel("Cumplimiento (%)")
ax.set_ylim(0, 80)
for bar, val in zip(bars, tasa.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
            f"{val:.1f}%", ha="center", fontsize=11, fontweight="bold")
ax.legend()

# -- G2: Distribución DBO salida por planta -----------------------------------
ax = axes[0, 1]
for planta, grp in df.groupby("planta"):
    ax.hist(grp["DBO_salida_mg_L"], bins=15, alpha=0.6,
            color=COLORES[planta], label=planta, edgecolor="white")
ax.axvline(30, color="red", linestyle="--", linewidth=1.5, label="Límite 30 mg/L")
ax.set_title("Distribución DBO Salida por Planta", fontweight="bold")
ax.set_xlabel("DBO Salida (mg/L)")
ax.set_ylabel("Frecuencia")
ax.legend()

# -- G3: Eficiencia DBO por planta (boxplot) ----------------------------------
ax = axes[1, 0]
plantas = df["planta"].unique()
data_box = [df[df["planta"] == p]["eficiencia_DBO"].values for p in plantas]
bp = ax.boxplot(data_box, labels=plantas, patch_artist=True,
                medianprops={"color": "white", "linewidth": 2})
for patch, planta in zip(bp["boxes"], plantas):
    patch.set_facecolor(COLORES[planta])
    patch.set_alpha(0.8)
ax.set_title("Eficiencia de Remoción DBO por Planta (%)", fontweight="bold")
ax.set_ylabel("Eficiencia (%)")

# -- G4: Caudal vs DBO salida (scatter) --------------------------------------
ax = axes[1, 1]
for planta, grp in df.groupby("planta"):
    ax.scatter(grp["caudal_entrada_m3_d"], grp["DBO_salida_mg_L"],
               color=COLORES[planta], alpha=0.5, label=planta, s=40)
# Regresión global
m, b, r, p_val, _ = stats.linregress(df["caudal_entrada_m3_d"], df["DBO_salida_mg_L"])
x_line = np.linspace(df["caudal_entrada_m3_d"].min(), df["caudal_entrada_m3_d"].max(), 100)
ax.plot(x_line, m * x_line + b, "k--", linewidth=1.5, label=f"Tendencia (r={r:.2f})")
ax.axhline(30, color="red", linestyle=":", linewidth=1.5, label="Límite 30 mg/L")
ax.set_title("Caudal de Entrada vs DBO Salida", fontweight="bold")
ax.set_xlabel("Caudal (m³/día)")
ax.set_ylabel("DBO Salida (mg/L)")
ax.legend(fontsize=8)

# -- G5: Evolución temporal de DBO salida -------------------------------------
ax = axes[2, 0]
for planta, grp in df.groupby("planta"):
    grp_sorted = grp.sort_values("fecha_registro")
    ax.plot(grp_sorted["fecha_registro"], grp_sorted["DBO_salida_mg_L"].rolling(7).mean(),
            color=COLORES[planta], label=planta, linewidth=2)
ax.axhline(30, color="red", linestyle="--", linewidth=1.5, label="Límite 30 mg/L")
ax.set_title("Tendencia DBO Salida (Media Móvil 7 días)", fontweight="bold")
ax.set_ylabel("DBO Salida (mg/L)")
ax.set_xlabel("Fecha")
ax.legend()
fig.autofmt_xdate()

# -- G6: Mapa de calor correlaciones ------------------------------------------
ax = axes[2, 1]
num_cols = ["caudal_entrada_m3_d", "DBO_entrada_mg_L", "SST_entrada_mg_L",
            "pH_entrada", "energia_aeracion_kWh", "lodos_generados_kg_d",
            "DBO_salida_mg_L", "eficiencia_DBO"]
corr_matrix = df[num_cols].corr(method="spearman")
labels = ["Caudal", "DBO ent.", "SST ent.", "pH", "Energía", "Lodos", "DBO sal.", "Efic."]
sns.heatmap(corr_matrix, ax=ax, annot=True, fmt=".2f", cmap="coolwarm",
            center=0, xticklabels=labels, yticklabels=labels,
            linewidths=0.5, annot_kws={"size": 8})
ax.set_title("Correlaciones de Spearman", fontweight="bold")
ax.tick_params(axis="x", rotation=45)
ax.tick_params(axis="y", rotation=0)

plt.tight_layout(rect=[0, 0, 1, 0.96])
dashboard_path = os.path.join(DASHBOARD, "dashboard_aqualimpia.png")
plt.savefig(dashboard_path, dpi=150, bbox_inches="tight")
plt.close()
print(f"✓ Dashboard guardado: {dashboard_path}")

# ==================================================================================
# 6. RESUMEN FINAL
# ==================================================================================
incumplimiento = (1 - resumen["tasa_cumplimiento"]) * 100
peor = incumplimiento.idxmax()
print("\n" + "=" * 60)
print("RESUMEN EJECUTIVO")
print("=" * 60)
print(f"  Tasa incumplimiento global : {df['cumplimiento_norma'].eq(0).mean()*100:.1f}%")
print(f"  Planta con más incumplimientos: {peor} ({incumplimiento[peor]:.1f}%)")
print(f"  DBO salida media global    : {df['DBO_salida_mg_L'].mean():.1f} mg/L")
print(f"  Eficiencia DBO media global: {df['eficiencia_DBO'].mean():.1f}%")
print("=" * 60)
print("\n✓ Análisis completado exitosamente.")