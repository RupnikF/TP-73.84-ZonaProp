import pandas as pd
import re
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from geopy.geocoders import OpenCage

API_KEY = "b508e874707d4e6d8c197569f77f3f80"
geolocator = OpenCage(API_KEY)

# 2. Procesar tipo de vivienda
def obtener_clase(valor):
    if pd.isnull(valor):
        return None
    return valor.split('·')[0].strip()

# 4. Procesar geocodificación1
def geocodear(direccion):
    try:
        dir = str(direccion[0]) + ', Argentina'
        ubicacion = geolocator.geocode(dir)
        if ubicacion:
            print(f'{ubicacion.latitude}, {ubicacion.longitude}')
            return ubicacion.latitude, ubicacion.longitude
        else:
            return None, None
    except Exception as e:
        #print(f"Error geocodificando la dirección {direccion}: {e}")
        return None, None

# 5. Procesar expensas
def convertir_expensas(valor):
    if pd.isnull(valor):
        return None
    if "No disponible" in valor:
        return None
    try:
        numero_str = valor.replace('Expensas $', '').strip().replace('.', '').replace(',', '')
        numero = int(numero_str)
        return numero
    except:
        return None

# 6. Extraer variables numéricas
def extraer_numero_regex(valor):
    if pd.isnull(valor):
        return None
    try:
        match = re.search(r'(\d+(?:[.,]\d+)?)', valor)
        if match:
            numero_str = match.group(1).replace(',', '.')
            if '.' in numero_str:
                return float(numero_str)
            else:
                return int(numero_str)
        else:
            return None
    except:
        return None



# 7. Procesar antigüedad
def convertir_antiguedad(valor):
    if pd.isnull(valor):
        return None
    if 'A estrenar' in valor:
        return 0
    try:
        match = re.search(r'\d+', valor)
        if match:
            return int(match.group(0))
        else:
            return None
    except:
        return None


# 8. Extraer características generales
def extract_plants(text):
    match = re.search(r'Cantidad plantas\s*:\s*(\d+|5 o más)', text)
    if match:
        if match.group(1) == '5 o más':
            return 5
        return int(match.group(1))
    return 1
def has_pool(text):
    return 'sí' if 'Pileta' in text else 'no'
def is_credit_compatible(text):
    return 'sí' if 'Apto profesional' in text else 'no'

# 13. Calcular precio promedio por m2 de propiedades cercanas
def calcular_precio_promedio_m2_cercano(row: pd.DataFrame, reference_data:pd.DataFrame):
    # Buscar la fila más cercana en latitud y longitud
    lat, lon = row['latitud'], row['longitud']
    ref_lat = reference_data['latitud']
    ref_lon = reference_data['longitud']
    dist = ((ref_lat - lat)**2 + (ref_lon - lon)**2).pow(0.5)
    idx_min = dist.idxmin()
    row['precio_m2_cercano'] = reference_data.loc[idx_min, 'precio_m2_cercano']
    return row

# 14. Imputar valores nulos
def handle_null_values(row:pd.DataFrame,reference_data:pd.DataFrame):
    columnas_media_round = ['antiguedad', 'dormitorios', 'baños', 'ambientes']
    columnas_media = ['m2_totales', 'm2_cubiertos', 'expenses', 'precio_m2_cercano']

    # Imputar expensas con 0 si es Casa
    if row['vivienda'].str.contains('Casa', case=False, na=False).any():
        row.loc[row['vivienda'].str.contains('Casa', case=False, na=False), 'expenses'] = row['expenses'].fillna(0)

    # Imputar columnas con media redondeada por tipo de vivienda
    for columna in columnas_media_round:
        media = reference_data.groupby('vivienda')[columna].mean().round()
        row[columna] = row.apply(
            lambda r: r[columna] if pd.notnull(r[columna]) else media.get(r['vivienda'], reference_data[columna].mean().round()),
            axis=1
        )

    # Imputar columnas con media por tipo de vivienda
    for columna in columnas_media:
        media = reference_data.groupby('vivienda')[columna].mean()
        row[columna] = row.apply(
            lambda r: r[columna] if pd.notnull(r[columna]) else media.get(r['vivienda'], reference_data[columna].mean()),
            axis=1
        )

    # Imputar cocheras con 0 si es nulo
    row['cocheras'] = row['cocheras'].fillna(0)

    return row

#Ahora no tenemos price
def process_single_row(row, scaler:StandardScaler, onehot_encoder:OneHotEncoder,reference_data:pd.DataFrame)-> pd.DataFrame | None:
    # Si es dict, convertir a DataFrame de una fila
    if isinstance(row, dict):
        row = pd.DataFrame([row])
    else:
        row = row.copy()

    # Procesar tipo de vivienda
    row['vivienda'] = row['title'].apply(obtener_clase)

    # Procesar geocodificación
    latitud,longitud = geocodear(row['location'])
    if latitud is None or longitud is None:
        return None
    row['latitud'] = latitud
    row['longitud'] = longitud

    # Procesar expensas
    row['expenses'] = row['expenses_price'].apply(convertir_expensas)

    # Extraer variables numéricas
    columnas_mapeo = {
        'icon-stotal': 'm2_totales',
        'icon-scubierta': 'm2_cubiertos',
        'icon-ambiente': 'ambientes',
        'icon-bano': 'baños',
        'icon-cochera': 'cocheras',
        'icon-dormitorio': 'dormitorios'
    }
    for col_original, col_nueva in columnas_mapeo.items():
        row[col_nueva] = row[col_original].apply(extraer_numero_regex)

    # Procesar antigüedad
    row['antiguedad'] = row['icon-antiguedad'].apply(convertir_antiguedad)

    # Extraer características generales
    row['general_features'] = row['general_features'].fillna('').astype(str)
    row['Cantidad_plantas'] = row['general_features'].apply(extract_plants)
    row['Pileta'] = row['general_features'].apply(has_pool)
    row['Apto_credito'] = row['general_features'].apply(is_credit_compatible)

    # Seleccionar columnas relevantes
    columns_to_keep = [
        'Cantidad_plantas', 'Pileta', 'Apto_credito', 'antiguedad', 'dormitorios',
        'cocheras', 'baños', 'ambientes', 'm2_totales', 'm2_cubiertos', 'expenses',
        'vivienda','latitud', 'longitud'
    ]
    row = row[columns_to_keep]

    # Imputar el precio por metro cuadrado cercano
    row = calcular_precio_promedio_m2_cercano(row, reference_data)
    # Imputar valores nulos con referencia a los datos
    row = handle_null_values(row, reference_data)

    # Estandarizar variables numéricas
    columnas_salida = ['Cantidad_plantas', 'antiguedad', 'dormitorios', 'cocheras', 'baños',
                       'ambientes', 'm2_totales', 'm2_cubiertos', 'expenses','latitud', 'longitud','precio_m2_cercano']
    scaled_values = scaler.transform(row[columnas_salida])
    df_scaled = pd.DataFrame(scaled_values, columns=columnas_salida, index=row.index)
    row[columnas_salida] = df_scaled

    # Codificar variables categóricas
    columnas_categoricas = ["Pileta", "Apto_credito", "vivienda"]
    encoded_data = onehot_encoder.transform(row[columnas_categoricas])
    feature_names = onehot_encoder.get_feature_names_out(columnas_categoricas)
    encoded_df = pd.DataFrame(encoded_data, columns=feature_names, index=row.index)
    row = row.drop(columns=columnas_categoricas)
    row = pd.concat([row, encoded_df], axis=1)

    return row