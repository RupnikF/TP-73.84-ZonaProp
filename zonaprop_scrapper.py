import time

from playwright.sync_api import sync_playwright

def scrape_zonaprop():
     with sync_playwright() as p:
        browser =  p.chromium.launch(headless=False)
        context = browser.new_context(user_agent="Mozilla/5.0 (...) Chrome/... Safari/...")
        page =  context.new_page()
        page.set_extra_http_headers({
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        })
        page.goto('https://www.zonaprop.com.ar/inmuebles-alquiler.html')

        #Get property cards
        property_cards = page.locator('div.postingCardLayout-module__posting-card-layout').all()

        # Loop through each property card and extract data
        for card in property_cards:
            link = card.get_attribute('data-to-posting')
            ## Go to the property page
            aux_page = context.new_page()
            aux_page.set_extra_http_headers({
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
            })
            aux_page.goto('https://www.zonaprop.com.ar/inmuebles-alquiler.html'+link)

            # Wait for the property details to load, id=article-container
            info_container = page.locator('div#article-container')

            # Extract the superficial info
            title = info_container.locator('div.title-type-sup-property').text_content().strip()
            rent_price = info_container.locator('div.price-container-property > div > div.price-value > span > span').text_content().strip()
            expenses_price = info_container.locator('div.price-container-property > div > div.price-extra > span').text_content().strip()
            location = info_container.locator('section#map-section > div.section-location-property > h4').text_content().strip()

            print(title)
            print(rent_price)
            print(expenses_price)
            print(location)

            break
        browser.close()


if __name__ == "__main__":
    scrape_zonaprop()
