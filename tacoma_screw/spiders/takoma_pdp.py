from scrapy.cmdline import execute
import scrapy
import json
import requests


class TakomaPdpSpider(scrapy.Spider):
    name = "takoma_pdp"

    def start_requests(self):
        url = (
            "https://www.tacomascrew.com/api/v1/products/dcfe4e9a-2523-4bc3-a6af-ab910150fb37?addToRecentlyViewed=true&applyPersonalization=true&categoryId=e7a0e6c0-a7cd-42a3-9f64-abfa01123b2a&expand=documents,specifications,styledproducts,htmlcontent,attributes,crosssells,pricing,relatedproducts,brand&getLastPurchase=true&includeAlternateInventory=true&includeAttributes=IncludeOnProduct,NotFromCategory&replaceProducts=false"
        )
        # url = (
        #     "https://www.tacomascrew.com/api/v1/products/936f4b1f-ace2-434e-b6b4-ab910151eae4"
        #     "?addToRecentlyViewed=true&applyPersonalization=true&expand=documents,specifications,"
        #     "styledproducts,htmlcontent,attributes,crosssells,pricing,relatedproducts,brand"
        #     "&getLastPurchase=true&includeAlternateInventory=true&includeAttributes=IncludeOnProduct,"
        #     "NotFromCategory&replaceProducts=false"
        # )
        cookies = {
            'CurrentLanguageId': 'a26095ef-c714-e311-ba31-d43d7e4e88b2',
            'SetContextLanguageCode': 'en-us',
            'CurrentCurrencyId': '30b432b9-a104-e511-96f5-ac9e17867f77',
            'SetContextPersonaIds': 'd06988c0-9358-4dbb-aa3d-b7be5b6a7fd9',
            'InsiteCacheId': 'c790567c-54ec-4c29-8667-b3e604b09d5a',
            '_gid': 'GA1.2.1328611644.1734097217',
            'CurrentFulfillmentMethod': 'Ship',
            'CurrentPickUpWarehouseId': '664fd364-efc6-40ad-9a1f-ab9800d1fa32',
            'FirstPage': 'false',
            'RecentlyViewedProducts': '%5b%7b%22Key%22%3a%22341-900%22%2c%22Value%22%3a%222024-12-13T13%3a41%3a51.0439739%2b00%3a00%22%7d%5d',
            '_ga_XZLHCD4MQE': 'GS1.1.1734097216.1.1.1734097312.0.0.0',
            '_ga': 'GA1.2.356651617.1734097217',
            '_dc_gtm_UA-38296018-1': '1',
        }
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9',
            'if-modified-since': 'Fri, 13 Dec 2024 13:41:51 GMT',
            'if-none-match': 'W/"c18b7958e9354e54bf058a62a325c300"',
            'priority': 'u=1, i',
            'referer': 'https://www.tacomascrew.com/Product/341-900',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }

        yield scrapy.Request(
            url=url,
            cookies=cookies,
            headers=headers,
            callback=self.parse
        )

    def parse(self, response):
        data = json.loads(response.body)
        product = data.get("product", {})
        product_id = product.get("id", "")

        # Extract required fields
        item = {
            "product_name": self.extract_product_name(product),
            "sku": self.extract_sku(product),
            "prices": self.extract_prices(product),
            "description": self.extract_description(product),
            "specification": self.extract_specification(product),
            "instock": self.extract_instock(product_id),
        }

        # Clean the data
        item = self.clean_data(item)

        # Log the item for debugging purposes
        self.log(f"Scraped Item: {json.dumps(item, indent=2)}")

    def extract_product_name(self, product):
        return {"Name": product.get("shortDescription", "")}

    def extract_sku(self, product):
        return {"Name": product.get("erpNumber", "")}

    def extract_prices(self, product):
        return {
            "Name": {
                "list_price": product.get("basicListPrice", 0.0),
                "sale_price": product.get("basicSalePrice", 0.0),
            }
        }

    def extract_description(self, product):
        html_content = product.get("htmlContent", "")
        return {"Name": html_content.split('•')}

    def extract_specification(self, product):
        return {
            "Name": {
                spec.get("label"): spec.get("attributeValues", [{}])[0].get("value", "")
                for spec in product.get("attributeTypes", []) if spec.get("attributeValues")
            }
        }

    def extract_instock(self, product_id):
        # Real-time inventory API call
        cookies = {
            'CurrentLanguageId': 'a26095ef-c714-e311-ba31-d43d7e4e88b2',
            'SetContextLanguageCode': 'en-us',
            'CurrentCurrencyId': '30b432b9-a104-e511-96f5-ac9e17867f77',
            'SetContextPersonaIds': 'd06988c0-9358-4dbb-aa3d-b7be5b6a7fd9',
            'InsiteCacheId': 'c790567c-54ec-4c29-8667-b3e604b09d5a',
        }
        headers = {
            'accept': 'application/json, text/plain, */*',
            'content-type': 'application/json;charset=UTF-8',
            'origin': 'https://www.tacomascrew.com',
            'referer': 'https://www.tacomascrew.com/product/442-108',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        }
        json_data = {
            'productIds': [product_id],
        }

        try:
            response = requests.post(
                'https://www.tacomascrew.com/api/v1/realtimeinventory',
                cookies=cookies,
                headers=headers,
                json=json_data
            )
            response_data = response.json()
            inventory = response_data.get("realTimeInventoryResults", [{}])[0]
            availability = inventory.get("inventoryAvailabilityDtos", [{}])[0]
            return {"Name": availability.get("availability", {}).get("message", "")}
        except Exception as e:
            self.log(f"Error fetching inventory: {e}")
            return {"Name": ""}

    def clean_data(self, item):
        def clean(value):
            if isinstance(value, dict):
                return {k: clean(v) for k, v in value.items() if v not in [None, ""]}
            elif isinstance(value, list):
                return [clean(v).strip() if isinstance(v, str) else clean(v) for v in value if v not in [None, ""]]
            elif isinstance(value, str):
                return value.strip()
            return value

        return clean(item)


if __name__ == '__main__':
    execute(f'scrapy crawl {TakomaPdpSpider.name}'.split())
