# TP-73.84-ZonaProp - Proyecto Scraper de ZonaProp

## Descripción
Este proyecto contiene scripts de Python para extraer información de propiedades en venta o alquiler desde el sitio web ZonaProp Argentina. Se implementan dos versiones diferentes de web scraping: una utilizando Playwright y otra con Selenium/undetected-chromedriver.

## Características
- Extracción de datos de propiedades incluyendo:
    - Título de la propiedad
    - Precio de venta/alquiler
    - Gastos adicionales (expensas)
    - Ubicación
    - Características generales de la propiedad
- Almacenamiento de datos en formato CSV
- Mecanismos anti-detección de bot
- Navegación por múltiples páginas de resultados

## Requisitos
```
python >= 3.7
pandas
selenium
undetected-chromedriver
playwright
```

## Instalación
```bash
pip install pandas selenium undetected-chromedriver playwright
playwright install chromium
```

## Uso
Para ejecutar el scraper basado en Selenium:
```bash
python zonaprop_scrapper_selenium.py
```

Para ejecutar el scraper basado en Playwright:
```bash
python zonaprop_scrapper.py
```

## Estructura
- `zonaprop_scrapper.py`: Implementación con Playwright -> No funciona pues no tiene medidas anti-detección
- `zonaprop_scrapper_selenium.py`: Implementación con Selenium y undetected-chromedriver

## Consideraciones
- El scraping web debe realizarse de manera ética y responsable
- Respete los términos de servicio del sitio web objetivo
- Utilice tiempos de espera aleatorios para evitar sobrecargar el servidor

## Resultado
El script generará un archivo CSV llamado `zonaprop_propiedades.csv` con los datos extraídos.