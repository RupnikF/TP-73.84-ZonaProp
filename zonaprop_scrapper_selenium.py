import random

import pandas as pd
from selenium.webdriver.common.by import By
import time
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_zonaprop():
    driver = uc.Chrome(headless=False,use_subprocess=False)

    # Set custom headers (Accept-Language)
    driver.get("https://www.zonaprop.com.ar/inmuebles-alquiler.html")

    # Get property cards
    property_cards = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.postingCardLayout-module__posting-card-layout'))
    )

    for card in property_cards:
        link = card.get_attribute('data-to-posting')
        print(link)
        if not link:
            continue

        driver.get('https://www.zonaprop.com.ar' + link)

        try:
            info_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'article-container'))
            )

            # Extract the superficial info
            title = info_container.find_element(By.CSS_SELECTOR, 'h2.title-type-sup-property').text.strip()
            rent_price = info_container.find_element(By.CSS_SELECTOR, 'div.price-container-property > div > div.price-value > span > span').text.strip()
            expenses_price = info_container.find_element(By.CSS_SELECTOR, 'div.price-container-property > div > div.price-extra > span').text.strip()
            location = info_container.find_element(By.CSS_SELECTOR, 'section#map-section > div.section-location-property > h4').text.strip()

            print(title)
            print(rent_price)
            print(expenses_price)
            print(location)
            # Extract features
            features_section = info_container.find_element(By.ID,'section-icon-features-property')
            features = features_section.find_elements(By.CSS_SELECTOR, 'li.icon-feature')
            for feature in features:
                feature_name = feature.find_element(By.CSS_SELECTOR, 'i').get_attribute('class').strip()
                feature_value = feature.text.strip()
                print(f"{feature_name}: {feature_value}")


        except Exception as e:
            print("Error extracting info:", e)
        break

    driver.quit()

def random_sleep(min_time=2, max_time=5):
    """Espera un tiempo aleatorio para simular comportamiento humano"""
    time.sleep(random.uniform(min_time, max_time))

def scrape_zonaprop_v2():
    # Lista para almacenar los datos
    property_data = []

    # Configuración del driver
    driver = uc.Chrome(headless=False, use_subprocess=False)

    try:
        # URL base y página inicial
        base_url = "https://www.zonaprop.com.ar/casas-departamentos-ph-venta.html"
        driver.get(base_url)
        random_sleep()

        # Número de páginas a scrapear (ajustar según necesidad)
        max_pages = 25
        page_number = 1

        while page_number < max_pages:
            print(f"Procesando página {page_number} de {max_pages}")

            # Obtener tarjetas de propiedades
            property_cards = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.postingCardLayout-module__posting-card-layout'))
            )

            # Guardar los enlaces antes de visitarlos
            property_links = []
            for i, card in enumerate(property_cards):
                link = card.get_attribute('data-to-posting')
                if link:
                    property_links.append(link)

            # Visitar cada propiedad
            for link in property_links:
                full_url = 'https://www.zonaprop.com.ar' + link

                driver.get(full_url)
                random_sleep(3, 6)


                try:
                    info_container = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, 'article-container'))
                    )

                    # Extraer información
                    property_info = {}
                    property_info['url'] = full_url

                    try:
                        property_info['title'] = info_container.find_element(By.CSS_SELECTOR, 'h2.title-type-sup-property').text.strip()
                    except:
                        property_info['title'] = "No disponible"

                    try:
                        property_info['rent_price'] = info_container.find_element(By.CSS_SELECTOR, 'div.price-container-property > div > div.price-value > span > span').text.strip()
                    except:
                        property_info['rent_price'] = "No disponible"

                    try:
                        property_info['expenses_price'] = info_container.find_element(By.CSS_SELECTOR, 'div.price-container-property > div > div.price-extra > span').text.strip()
                    except:
                        property_info['expenses_price'] = "No disponible"

                    try:
                        property_info['location'] = info_container.find_element(By.CSS_SELECTOR, 'section#map-section > div.section-location-property > h4').text.strip()
                    except:
                        property_info['location'] = "No disponible"

                    # Extraer características
                    try:
                        features_section = info_container.find_element(By.ID, 'section-icon-features-property')
                        features = features_section.find_elements(By.CSS_SELECTOR, 'li.icon-feature')
                        for feature in features:
                            feature_name = feature.find_element(By.CSS_SELECTOR, 'i').get_attribute('class').strip()
                            feature_value = feature.text.strip()
                            property_info[feature_name] = feature_value
                    except:
                        property_info['features'] = "No disponible"

                    try:
                        # Desplazamiento suave hacia abajo para hacer visibles más elementos
                        driver.execute_script("window.scrollBy(0, 1500);")
                        # Pequeña pausa para permitir que la página responda
                        time.sleep(1.5)
                        # Alternativa con XPath
                        general_features = []
                        feature_spans = info_container.find_elements(By.XPATH, '//span[contains(@class, "generalFeaturesProperty-module__description-text")]')

                        for span in feature_spans:
                            general_features.append(span.text.strip())

                        property_info['general_features'] = "; ".join(general_features)
                    except Exception as e:
                        property_info['general_features'] = "No disponible"
                        print(f"Error extrayendo características generales: {e}")

                    # Guardar datos
                    property_data.append(property_info)
                    print(f"Información extraída para: {property_info.get('title', 'propiedad sin título')}")

                except Exception as e:
                    print(f"Error extrayendo información: {e}")

                random_sleep(1, 2)

            # Ir a la siguiente página si no es la última
            if page_number < max_pages:
                try:
                    driver.get(f"https://www.zonaprop.com.ar/casas-departamentos-ph-venta-pagina-{page_number + 1}.html")
                    page_number += 1
                    random_sleep(3, 4)  # Espera más larga entre páginas
                except Exception as e:
                    print("No se pudo avanzar a la siguiente página")
                    break

    except Exception as e:
        print(f"Error general: {e}")

    finally:
        # Guardar los datos recolectados
        if property_data:
            df = pd.DataFrame(property_data)
            df.to_csv('zonaprop_propiedades.csv', index=False)
            print(f"Se guardaron {len(property_data)} propiedades en zonaprop_propiedades.csv")

        # Cerrar el navegador
        driver.quit()


if __name__ == "__main__":
    #scrape_zonaprop()
    scrape_zonaprop_v2()

