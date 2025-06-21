# TP Ciencia de Datos - Prophetario  

Este proyecto tiene como objetivo predecir el valor de propiedades en Argentina utilizando un enfoque basado en aprendizaje automático. Se emplea una primer estapa de recopialción de datos mediante web scrapper en el sitio ZonaProp y una segundo instancia con un pipeline completo de procesamiento de datos, selección de variables, entrenamiento y evaluación de modelos para estimar el precio con buena precisión.

# Modelo de Predicción

El modelo principal utilizado es un `LGBMRegressor` (Light Gradient Boosting Machine), un algoritmo de boosting que combina múltiples árboles de decisión para mejorar el rendimiento y la capacidad de generalización. El modelo fue entrenado sobre un conjunto de datos enriquecido con variables significativas como cantidad de ambientes, m2 cubiertos, ubicación (latitud y longitud), antigüedad y amenities, entre otras.

### Descripción

El pipeline implementado realiza los siguientes pasos:

- Carga y limpieza del dataset obtenido del web scrapper.
- Filtrado de outliers y normalización de datos.
- División entre datos de entrenamiento y test.
- Entrenamiento del modelo.
- Evaluación con métricas como R², MAE y RMSE.
- Visualización de predicciones y análisis de errores.
- Reflexiones finales.

### Funcionalidades

- Predicción de precios de propiedades con alta precisión.
- Evaluación automática de métricas de desempeño.
- Preprocesamiento completo y ajustable del dataset.
- Gráficos de comparación entre valores reales y predichos.
- Posibilidad de guardar el modelo entrenado para futuras predicciones.

### Requisitos

- Python 3.8 o superior
- Pandas
- Numpy
- Scikit-learn
- Matplotlib
- Seaborn


### Instalación

    pip install pandas numpy scikit-learn lightgbm matplotlib seaborn

### Uso

Para ejecutar el pipeline de predicción de precios de propiedades:

1. Asegurate de tener el archivo `zonaprop_propiedades.csv` en la raiz del directorio o generarlo mediante `zonaprop_scapper_selenium.py`.
2. Abrí y corré el notebook `pipeline_completo.ipynb` en Jupyter, VSCode o Google Colab.
3. El pipeline entrenará el modelo `LGBMRegressor`, evaluará su rendimiento, y filtrará predicciones confiables (±10% de error).


### Resultado

- Se generan gráficos que comparan valores reales vs. predichos.
- El modelo produce un error de:
    - MAE: 39047.10
    - MSE: 3156020017.02
    - RMSE: 56178.47
    - R2: 0.68



# Scraper de ZonaProp

### Descripción
Esta sección explica el funcionamiento de los scripts de Python para extraer información de propiedades en venta desde el sitio web ZonaProp Argentina.

### Funcionalidades
- Almacenamiento de datos en formato CSV
- Mecanismos anti-detección de bot
- Navegación por múltiples páginas de resultados
- Extracción de datos de propiedades incluyendo:
    - Antigüedad (Numérico): Años de antigüedad, si l es nueva se utiliza 0.
    - Dormitorios (Numérico): Cantidad de dormitorios disponibles en la propiedad.
    - Baños (Numérico): Cantidad total de baños en la propiedad.
    - Ambientes (Numérico): Número total de ambientes (dormitorios, salas, cocinas, etc.).
    - Superficie_total_m2 (Numérico): Superficie total en metros cuadrados
    - Superficie_cubierta_m2 (Numérico): Superficie construida en metros cuadrados.
    - Expensas (Numérico): Expensas mensuales de la vivienda, en pesos argentinos.
    - Precio (Numérico): Precio de venta de la propiedad.
    - Pileta (Categórico - Sí/No): Indica si la propiedad tiene pileta.
    - Apto_credito (Categórico - Sí/No): Indica si es apta para crédito hipotecario.
    - Cantidad_plantas (Numérico): Número de plantas en la propiedad.
    - Vivienda (Categórico): "Casa", "Departamento", "PH", "Dúplex", etc.
    - Cocheras (Numérico): Cantidad de cocheras o lugares para estacionamiento.


### Requisitos
```
python >= 3.7
pandas
selenium
undetected-chromedriver
playwright
```

### Instalación
```bash
pip install pandas selenium undetected-chromedriver playwright
playwright install chromium
```

### Uso
Para ejecutar el scraper basado en Selenium:
```bash
python zonaprop_scrapper_selenium.py
```

### Consideraciones
- El scraping web debe realizarse de manera ética y responsable
- Utilice tiempos de espera aleatorios para evitar sobrecargar el servidor

### Resultado
El script generará un archivo CSV llamado `zonaprop_propiedades.csv` con los datos extraídos.