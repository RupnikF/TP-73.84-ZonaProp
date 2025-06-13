import pandas as pd
import numpy as np
import re
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
import joblib


# 2. Procesar tipo de vivienda
def obtener_clase(valor):
    if pd.isnull(valor):
        return None
    return valor.split('·')[0].strip()

# 3. Procesar precio
ARS_TO_USD = 1 / 1200
def convertir_precio(valor):
    if pd.isnull(valor):
        return None
    try:
        partes = valor.split()
        moneda = partes[0]
        numero_str = partes[1].replace('.', '').replace(',', '')
        numero = int(numero_str)
        if moneda == 'USD':
            return numero
        elif moneda == 'ARS':
            return int(numero * ARS_TO_USD)
        else:
            return None
    except:
        return None


# 4. Procesar expensas
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


# 5. Extraer variables numéricas
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



# 6. Procesar antigüedad
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


# 7. Extraer características generales
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


# 9. Eliminar outliers extremos (3*IQR)
def get_extreme_outliers(df, column):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 3 * IQR
    upper_bound = Q3 + 3 * IQR
    outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
    return outliers

def handle_outliers(data:pd.DataFrame):
    columns_numeric = ['price', 'm2_totales', 'm2_cubiertos', 'dormitorios', 'baños', 'antiguedad']
    extreme_outliers = pd.DataFrame()
    for column in columns_numeric:
        outliers = get_extreme_outliers(data, column)
        extreme_outliers = pd.concat([extreme_outliers, outliers])
    extreme_outliers = extreme_outliers.drop_duplicates()
    data = data.drop(index=extreme_outliers.index)
    return data




# 12. Imputar valores nulos
def handle_null_values(data:pd.DataFrame):
    columnas_media = ['antiguedad', 'dormitorios', 'baños', 'ambientes', 'm2_totales', 'm2_cubiertos','expenses']
    mask_casas = data['vivienda'].str.contains('Casa', case=False, na=False)
    data.loc[mask_casas, 'expenses'] = data.loc[mask_casas, 'expenses'].fillna(0)
    for columna in columnas_media:
        data[columna] = data.groupby('vivienda')[columna].transform(lambda x: x.fillna(round(x.mean(), 0)))
    data['cocheras'] = data['cocheras'].fillna(0)
    data = data.dropna(subset=['price'])
    return data



# 13. Estandarizar variables numéricas
def standarize_numeric_columns(data:pd.DataFrame):
    columnas_salida = ['Cantidad_plantas', 'antiguedad', 'dormitorios', 'cocheras', 'baños',
                       'ambientes', 'm2_totales', 'm2_cubiertos', 'expenses', 'price']
    scaler = MinMaxScaler()
    scaled_values = scaler.fit_transform(data[columnas_salida])
    df_scaled = pd.DataFrame(scaled_values, columns=columnas_salida, index=data.index)
    data[columnas_salida] = df_scaled
    return data,scaler

def standarize_numeric_columns_transform(data:pd.DataFrame, scaler:MinMaxScaler):
    columnas_salida = ['Cantidad_plantas', 'antiguedad', 'dormitorios', 'cocheras', 'baños',
                       'ambientes', 'm2_totales', 'm2_cubiertos', 'expenses']
    scaled_values = scaler.transform(data[columnas_salida])
    data[columnas_salida] = pd.DataFrame(scaled_values, columns=columnas_salida, index=data.index)
    #Logaritmo en la variable objetivo 'price'
    data['price'] = np.log1p(data['price'])
    return data

# 14. Codificar variables categóricas
def encode_categorical_columns(data:pd.DataFrame):
    columnas_categoricas = ["Pileta","Apto_credito","vivienda"]
    onehot_encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore', drop="first")
    encoded_data = onehot_encoder.fit_transform(data[columnas_categoricas])
    feature_names = onehot_encoder.get_feature_names_out(columnas_categoricas)
    encoded_df = pd.DataFrame(encoded_data, columns=feature_names, index=data.index)
    data = data.drop(columns=columnas_categoricas)
    data = pd.concat([data, encoded_df], axis=1)
    return data, onehot_encoder

# 15. Guardar el dataset final y los objetos de transformación
def dump_data(data:pd.DataFrame, scaler, onehot_encoder):
    # Guardar el dataset final
    data.to_csv("dataset.csv", index=False)
    # Guardar los objetos de transformación
    joblib.dump(scaler, 'minmaxscaler.joblib')
    joblib.dump(onehot_encoder, 'onehotencoder.joblib')

def process_data_from_csv(csv_path:str):
    # 1. Cargar el dataset
    data = pd.read_csv(csv_path)

    # 2. Procesar tipo de vivienda
    data['vivienda'] = data['title'].apply(obtener_clase)
    # 3. Procesar precio
    data['price'] = data['rent_price'].apply(convertir_precio)
    # 4. Procesar expensas
    data['expenses'] = data['expenses_price'].apply(convertir_expensas)

    # 5. Extraer variables numéricas
    columnas_mapeo = {
        'icon-stotal': 'm2_totales',
        'icon-scubierta': 'm2_cubiertos',
        'icon-ambiente': 'ambientes',
        'icon-bano': 'baños',
        'icon-cochera': 'cocheras',
        'icon-dormitorio': 'dormitorios'
    }
    for col_original, col_nueva in columnas_mapeo.items():
        data[col_nueva] = data[col_original].apply(extraer_numero_regex)

    # 6. Procesar antigüedad
    data['antiguedad'] = data['icon-antiguedad'].apply(convertir_antiguedad)

    # 7. Extraer características generales
    data['general_features'] = data['general_features'].fillna('').astype(str)
    data['Cantidad_plantas'] = data['general_features'].apply(extract_plants)
    data['Pileta'] = data['general_features'].apply(has_pool)
    data['Apto_credito'] = data['general_features'].apply(is_credit_compatible)

    # 8. Seleccionar columnas relevantes
    columns_to_keep = [
        'Cantidad_plantas', 'Pileta', 'Apto_credito', 'antiguedad', 'dormitorios',
        'cocheras', 'baños', 'ambientes', 'm2_totales', 'm2_cubiertos', 'expenses',
        'price', 'vivienda'
    ]
    data = data[columns_to_keep]

    # 9. Eliminar outliers extremos (3*IQR)
    data = handle_outliers(data)

    # 10. Eliminar duplicados
    data = data.drop_duplicates()

    # 11. Eliminar filas con "No disponible" en vivienda
    data = data[~data["vivienda"].str.strip().str.lower().eq("no disponible")]

    # 12. Imputar valores nulos
    data = handle_null_values(data)

    # 13. Estandarizar variables numéricas
    data, scaler = standarize_numeric_columns(data)
    # 14. Codificar variables categóricas
    data, onehot_encoder = encode_categorical_columns(data)

    # 15. Guardar el dataset final y los objetos de transformación
    dump_data(data, scaler, onehot_encoder)
    return data


def process_single_row(row, scaler:MinMaxScaler, onehot_encoder:OneHotEncoder):
    # Si es dict, convertir a DataFrame de una fila
    if isinstance(row, dict):
        row = pd.DataFrame([row])
    else:
        row = row.copy()

    # Procesar tipo de vivienda
    row['vivienda'] = row['title'].apply(obtener_clase)
    # Procesar precio
    row['price'] = row['rent_price'].apply(convertir_precio)
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
        'price', 'vivienda'
    ]
    row = row[columns_to_keep]

    # Imputar valores nulos (con 0, ya que no hay grupo para promedios)
    for col in ['antiguedad', 'dormitorios', 'baños', 'ambientes', 'm2_totales', 'm2_cubiertos', 'expenses', 'cocheras']:
        row[col] = row[col].fillna(0)
    row = row.dropna(subset=['price'])

    # Estandarizar variables numéricas
    columnas_salida = ['Cantidad_plantas', 'antiguedad', 'dormitorios', 'cocheras', 'baños',
                       'ambientes', 'm2_totales', 'm2_cubiertos', 'expenses', 'price']
    row[columnas_salida] = scaler.transform(row[columnas_salida])

    # Codificar variables categóricas
    columnas_categoricas = ["Pileta", "Apto_credito", "vivienda"]
    encoded_data = onehot_encoder.transform(row[columnas_categoricas])
    feature_names = onehot_encoder.get_feature_names_out(columnas_categoricas)
    encoded_df = pd.DataFrame(encoded_data, columns=feature_names, index=row.index)
    row = row.drop(columns=columnas_categoricas)
    row = pd.concat([row, encoded_df], axis=1)

    return row