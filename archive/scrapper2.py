import scrapy
from scrapy import Selector
from playwright.sync_api import sync_playwright
import time
import logging

class MagicpinSpider(scrapy.Spider):
    name = 'magicpin'
    
    def start_requests(self):
        # Here, we'll accept the URL from the function argument
        url = getattr(self, 'url', None)
        if url:
            yield scrapy.Request(url=url, callback=self.parse)
    
    def parse(self, response):
        start_parse = time.time()
        self.logger.info("Parsing Started")
        delivery_url, hotel_name = self.delivery_url_extractor(response.text)
        self.logger.info("Delivery URL Extracted")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.route('**/*.{css*,woff,woff2,png,jpg,jpeg,gif,svg}', lambda route: route.abort())

            page.goto(delivery_url)
            # Define the selector to wait for
            selector = '.catalogItemsHolder .categoryListing:not(:first-child) .itemDetails'
            # Specify the maximum time to wait (in seconds)
            timeout = 30000
            
            # Wait for the expected number of elements to appear
            page.wait_for_selector(selector, state='attached', timeout=timeout)
            self.logger.info("Selector Found")
            # html_content=page.content()
            # Wait for a brief moment to ensure all elements have loaded
            time.sleep(0.5)
            item_details_divs = page.query_selector_all('.catalogItemsHolder .categoryListing:not(:first-child) .itemDetails')
            item_data = []
            for div in item_details_divs:
                try:
                    item_name_element = div.query_selector('.itemName a.rel-handled')
                    item_name = item_name_element.inner_text()
                except Exception as e:
                    self.logger.error(f"An exception occurred at itemName: {str(e)}")
                    return item_data
                try:
                    item_price_element = div.query_selector('.itemPrice.nonDiscountedPrice')
                    mrp_str = item_price_element.inner_text()
                except Exception:
                    try:
                        item_price_element = div.query_selector('.itemPrice')
                        mrp_str = item_price_element.inner_text()
                    except Exception as e:
                        self.logger.error(f"An exception occurred at mrp: {str(e)}")
                        return item_data
                try:
                    mrp = int(mrp_str.replace('₹', ''))
                except Exception as e:
                    self.logger.error(f"An exception occurred at mrp ₹ to int conversion: {str(e)}")
                    return item_data
                item_data.append({"item_name": item_name, "mrp": mrp})
            browser.close()
            self.logger.info("Scraping Completed")
            stop_parse = time.time()
            self.logger.info(f"Scraper took {stop_parse - start_parse} seconds")
            
        return {'item_data': item_data, 'hotel_name': hotel_name}

    def delivery_url_extractor(self, html_text):
        selector = Selector(text=html_text)
        delivery_tab = selector.css('a.delivery-tab')
        hotel_tab = selector.css('h1.v2 a::text')
        hotel_name = hotel_tab.get()
        if delivery_tab:
            delivery_href = delivery_tab.attrib['href']
            return [delivery_href, hotel_name]

# Configure logging
logging.basicConfig(level=logging.INFO)
