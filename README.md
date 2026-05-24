# AquaLimpia S.A. — Proyecto de Ciencia de Datos
## Análisis de Desempeño de Plantas de Tratamiento de Aguas Residuales

---

## Objetivos del Proyecto

1. **Identificar patrones** de incumplimiento normativo en parámetros de DBO del efluente tratado.
2. **Evaluar la eficiencia** de remoción de contaminantes en tres plantas (Norte, Centro, Sur).
3. **Detectar alertas operativas** relacionadas con variaciones de caudal y carga contaminante.
4. **Generar evidencia analítica reproducible** para respaldar informes ambientales ante organismos fiscalizadores.
5. **Priorizar acciones correctivas** mediante análisis estadístico multivariado.

---

## Preguntas de Investigación

- ¿Cuáles plantas presentan mayor tasa de incumplimiento de la norma de DBO?
- ¿Existe correlación estadística entre el caudal de entrada y la DBO del efluente tratado?
- ¿La distribución de la DBO de salida sigue una distribución normal?
- ¿Qué variables operativas explican mejor la eficiencia de tratamiento?

---

## Estructura del Repositorio

```
aqualimpia/
├── data/
│   └── dataset_set_A_aguas_residuales.xlsx   # Dataset original
├── scripts/
│   ├── utils.py                               # Módulo reutilizable (NumPy, SciPy, Joblib)
│   └── analisis_aqualimpia.py                 # Script principal de análisis
├── outputs/
│   ├── area_operaciones.xlsx                  # Salida para Área de Operaciones
│   └── area_gestion_ambiental.xlsx            # Salida para Gestión Ambiental
├── dashboard/
│   └── dashboard_aqualimpia.png               # Dashboard exploratorio (6 gráficos)
└── docs/
    └── README.md                              # Esta documentación
```

---

## Librerías y Configuración

| Librería | Versión mínima | Uso |
|----------|---------------|-----|
| pandas | 2.0 | Carga, transformación y agrupación de datos |
| numpy | 1.24 | Estadísticas vectorizadas, arrays |
| scipy | 1.10 | Shapiro-Wilk, correlación Spearman, regresión |
| joblib | 1.3 | Procesamiento paralelo de columnas numéricas |
| matplotlib | 3.7 | Generación del dashboard (6 gráficos) |
| seaborn | 0.12 | Heatmap de correlaciones |
| openpyxl | 3.1 | Lectura/escritura de archivos Excel |

**Instalación:**
```bash
pip install pandas numpy scipy joblib matplotlib seaborn openpyxl
```

**Ejecución:**
```bash
python scripts/analisis_aqualimpia.py
```

---

## Flujo de Trabajo Reproducible

```
[Dataset XLSX]
      │
      ▼
1. cargar_dataset()       ← parsea fechas, ordena cronológicamente
      │
      ▼
2. evaluar_calidad()      ← nulos, duplicados, outliers IQR, validaciones dominio
      │
      ▼
3. calcular_eficiencia_dbo()   ← ((DBO_entrada - DBO_salida) / DBO_entrada) × 100
      │
      ▼
4. estadisticas_numpy()        ← media, mediana, std, percentiles (NumPy)
   estadisticas_todas_columnas() ← Joblib paralelo
   prueba_normalidad()          ← Shapiro-Wilk (SciPy)
   correlacion_spearman()       ← ρ de Spearman (SciPy)
      │
      ├──► generar_archivo_operaciones()   → area_operaciones.xlsx
      ├──► generar_archivo_ambiental()     → area_gestion_ambiental.xlsx
      └──► Dashboard (6 gráficos)          → dashboard_aqualimpia.png
```

---

## Resultados Principales

### Cumplimiento Normativo
- **Tasa de incumplimiento global: 77.5%** — solo el 22.5% de los registros cumplen la norma de DBO ≤ 30 mg/L.
- **Planta Norte** presenta la mayor tasa de incumplimiento (83%).
- **Planta Sur** es la de mejor desempeño relativo (70% de incumplimiento).

### DBO del Efluente
- DBO salida media: **36.2 mg/L** (límite normativo = 30 mg/L).
- La distribución **no es normal** (Shapiro-Wilk, p=0.01), lo que justifica el uso de estadísticos no paramétricos.

### Correlaciones
- No hay correlación estadísticamente significativa entre caudal de entrada y DBO de salida (ρ=0.11, p=0.13).
- Tampoco entre DBO de entrada y eficiencia de remoción (ρ=-0.02, p=0.74).
- Esto sugiere que las desviaciones obedecen a factores operativos internos, no solo a la carga entrante.

### Eficiencia de Remoción
- Eficiencia media global de DBO: **87.1%** — técnicamente aceptable, pero la alta DBO de entrada produce un efluente que aún supera el límite.

---

## Calidad de los Datos

| Indicador | Resultado |
|-----------|-----------|
| Registros totales | 200 |
| Valores nulos | 0 |
| Registros duplicados | 0 |
| Outliers (caudal) | 2 |
| Outliers (energía aireación) | 3 |
| Outliers (lodos) | 2 |
| Outliers (DBO salida) | 2 |
| Advertencias de dominio | Ninguna |

**Limitaciones identificadas:**
- Los outliers en energía y caudal podrían indicar registros de condiciones de arranque/parada.
- El período cubre solo un trimestre (Jul–Oct 2025), limitando la generalización estacional.
- No se dispone de datos de temperatura del agua, que es un factor relevante en la eficiencia biológica.
- El indicador `cumplimiento_norma` es binario; no captura la magnitud del incumplimiento.

---

## Referencias

- McKinney, W. (2022). *Python for Data Analysis* (3.ª ed.). O'Reilly.
- Virtanen, P. et al. (2020). SciPy 1.0: Fundamental algorithms for scientific computing. *Nature Methods, 17*, 261–272.
- IACC. (2025). *Ciencia de Datos. Semana 8*. Instituto Profesional IACC.
- Decreto Supremo N°90 (2000). Establece norma de emisión para la regulación de contaminantes asociados a las descargas de residuos líquidos a aguas marinas y continentales superficiales. 
Puntos clave del decreto:
Límites máximos permisibles: Establece los estándares (LMP) de concentración para diversos contaminantes (físicos, químicos y biológicos) que pueden contener los riles (residuos industriales líquidos) antes de ser vertidos.
Cuerpos receptores: Aplica a descargas realizadas en ríos, lagos, embalses, estuarios, y el mar. 
Monitoreo obligatorio: Exige a las empresas y actividades reguladas medir sus niveles de emisión y reportarlos a las autoridades fiscalizadoras
Ministerio Secretaría General de la Presidencia de Chile.
