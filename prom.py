import pandas as pd
import numpy as np

# Cargar el CSV
df = pd.read_csv('dataset_final.csv')  # Reemplazá con la ruta real

# Calcular promedio y desviación estándar
promedio = np.expm1(df['price'].mean())
desvio = df['price'].std()
relativo = desvio / df['price'].mean() 
promedio_error = relativo * promedio
print(f"📈 Promedio de error: ${promedio_error:,.2f}")
print(f"📊 Promedio de price: ${promedio:,.2f}")
print(f"📉 Desviación estándar: ${desvio:,.2f}")

