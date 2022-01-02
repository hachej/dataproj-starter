
import json

NOTION_TOKEN = "secret_3gClGYW5hUFCQlVNeDlFDhEvwLe9WTHXHsYANzof9qG"
headers = {
    "Authorization": "Bearer " + NOTION_TOKEN,
    "Content-Type": "application/json",
    "Notion-Version": "2021-08-16"
}
import requests
import logging 

class Notion:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def query(self, database_id, filter={}):
        readUrl = f"https://api.notion.com/v1/databases/{database_id}/query"
        start_cursor = None
        has_more = True
        results = []

        while has_more:

            if start_cursor:
                filter["start_cursor"] = start_cursor

            res = requests.request("POST", readUrl, headers=headers, data = json.dumps(filter))
            data = res.json()

            if res.status_code != 200:
                self.logger.error(json.dumps(data))
                raise

            results += data["results"]
            has_more = data["has_more"]

            if has_more:
                start_cursor = data["next_cursor"]

        self.logger.info(f"{len(results)} downloaded")
        return results

    def insert(self, database_id, properties):
        page = {
            'object': 'page',
            'parent': {'type': 'database_id','database_id': database_id},
            'properties': properties
        }
        readUrl = f"https://api.notion.com/v1/pages"
        res = requests.request("POST", readUrl, headers=headers, data=json.dumps(page))
        data = res.json()
        if res.status_code != 200:
            print(properties)
            self.logger.error(json.dumps(data))
            raise
        return data["id"]