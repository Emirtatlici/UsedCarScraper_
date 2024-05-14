import requests
import pandas as pd 
from pandas import json_normalize
import logging
import signal

class CarSearch:
    def __init__(self):
        self.data = pd.DataFrame()  
        self.base_url = "https://cars.usnews.com/ajax/inventory/used-cars/search"  
        self.headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9,tr-TR;q=0.8,tr;q=0.7",
            "referer": "https://cars.usnews.com/cars-trucks/used-cars/for-sale",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "Windows",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        }
        self.columns_to_exclude = ['carfax_one_owner', 'has_free_carfax_report', 'first_image_url', 'external_listing_url', 
                                    'unique_id', 'detail_button_text', 'vin', 'dealer_phone', 'dealer_name', 'carfax_url', 
                                    'primary_category_rank', 'primary_category_name', 'primary_category_url', 'review_url', 
                                    'detail_url', 'carfax_token', 'carfax_free_report']  
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.exit_gracefully = False  

    def signal_handler(self, signum, frame):
        self.logger.info("Signal received. Saving the scraped data before exiting...")
        self.exit_gracefully = True

    def search_cars(self):
        signal.signal(signal.SIGINT, self.signal_handler)  
        try:
            print("Enter search parameters:")
            pagenumber = int(input("Page number: "))
            price_max = input("Maximum price: ")
            mileage_max = input("Maximum mileage: ")
            year_min = input("Minimum year: ")
            year_max = input("Maximum year: ")
            zip_code = input("ZIP Code (press Enter to use default '90001'): ") or "90001"
            
            # Print entered parameters
            print("\nEntered search parameters:")
            print(f"Page number: {pagenumber}")
            print(f"Maximum price: {price_max}")
            print(f"Maximum mileage: {mileage_max}")
            print(f"Minimum year: {year_min}")
            print(f"Maximum year: {year_max}")
            print(f"ZIP Code: {zip_code}\n")
            
            print("Searching...\n")
            
            for page in range(1, pagenumber + 1):
                querystring = {
                    "range": "50",
                    "price_max": price_max,
                    "mileage_max": mileage_max,
                    "used_checked": "1",
                    "zip": zip_code,
                    "year_min": year_min,
                    "year_max": year_max,
                    "sort": "0",
                    "page": page
                }
                response = requests.get(self.base_url, headers=self.headers, params=querystring, timeout=10)  
                response.raise_for_status()  
                temp = response.json()
                normalize = json_normalize(temp["data"]["listings"])
                
                # Exclude specified columns
                normalize = normalize.drop(columns=self.columns_to_exclude, errors='ignore')
                
                if not self.data.empty:
                    self.data = pd.concat([self.data, normalize], ignore_index=True)
                else:
                    self.data = normalize
                self.logger.info(f"Page {page} scraped. {pagenumber - page} pages left.")
                if self.exit_gracefully:
                    break  
        except (requests.RequestException, ConnectionError, TimeoutError) as e:
            self.logger.error(f"An error occurred: {e}")
        finally:
            return self.data  
