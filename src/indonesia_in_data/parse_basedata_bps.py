# Get and store all data from BPS Web API

import json
import os
import requests
from pymongo import MongoClient


class BPS_API:
    def __init__(self):
        # Initialize mongodb
        self.client = MongoClient(os.environ["MONGODB_URI"])
        self.database = self.client["bps_database"]

    def all_domains(self):
        # Get all domains from BPS API
        params = {"type": "all", "key": os.environ["BPS_API_KEY"]}
        response = requests.get(
            url="https://webapi.bps.go.id/v1/api/domain", params=params
        )
        domains = json.loads(response.text)["data"][1]

        # Store to database
        collection = self.database["domains"]
        for domain in domains:
            domain_id = domain["domain_id"]
            # Define filters based on domain_id
            filter = {"domain_id": f"{domain_id}"}

            # Determine values to be updated
            values = {"$set": domain}

            # Update values to database
            collection.update_one(filter=filter, update=values, upsert=True)

    def all_subjects(self):
        # Get all domains from database
        collection = self.database["domains"]
        domains = list(collection.find({}))

        # Get all subjects from BPS API for each domain
        # Create collection
        collection = self.database["subjects"]
        for domain in domains:
            domain_id = domain["domain_id"]
            dict = {}
            dict["domain_id"] = domain_id
            params = {
                "model": "subject",
                "domain": f"{domain_id}",
                "key": os.environ["BPS_API_KEY"],
            }
            response = requests.get(
                url="https://webapi.bps.go.id/v1/api/list", params=params
            )
            subjects_metadata = json.loads(response.text)["data"][0]
            total_pages = subjects_metadata["pages"]

            dict["data"] = []

            for page in range(1, total_pages + 1):
                params = {
                    "model": "subject",
                    "domain": f"{domain_id}",
                    "page": f"{page}",
                    "key": os.environ["BPS_API_KEY"],
                }
                response = requests.get(
                    url="https://webapi.bps.go.id/v1/api/list", params=params
                )
                response_json = json.loads(response.text)
                if response_json["data-availability"] == "available":
                    dict["data"].extend(response_json["data"][1])
                elif response_json["data-availability"] == "list-not-available":
                    pass

            # Define filters based on domain_id
            filter = {"domain_id": f"{domain_id}"}

            # Determine values to be updated
            values = {"$set": dict}

            # Update values to database
            collection.update_one(filter=filter, update=values, upsert=True)

    def all_variables(self):
        # Get all domains from database
        collection = self.database["domains"]
        domains = list(collection.find({}))

        # Get all variables from BPS API for each domain
        # Create collection
        collection = self.database["variables"]
        for domain in domains:
            domain_id = domain["domain_id"]
            dict = {}
            dict["domain_id"] = domain_id
            params = {
                "model": "var",
                "domain": f"{domain_id}",
                "key": os.environ["BPS_API_KEY"],
            }
            response = requests.get(
                url="https://webapi.bps.go.id/v1/api/list", params=params
            )
            subjects_metadata = json.loads(response.text)["data"][0]
            total_pages = subjects_metadata["pages"]

            dict["data"] = []

            for page in range(1, total_pages + 1):
                params = {
                    "model": "var",
                    "domain": f"{domain_id}",
                    "page": f"{page}",
                    "key": os.environ["BPS_API_KEY"],
                }
                response = requests.get(
                    url="https://webapi.bps.go.id/v1/api/list", params=params
                )
                response_json = json.loads(response.text)
                if response_json["data-availability"] == "available":
                    dict["data"].extend(response_json["data"][1])
                elif response_json["data-availability"] == "list-not-available":
                    pass

            # Define filters based on domain_id
            filter = {"domain_id": f"{domain_id}"}

            # Determine values to be updated
            values = {"$set": dict}

            # Update values to database
            collection.update_one(filter=filter, update=values, upsert=True)


def main():
    bps_api = BPS_API()

    # Get and store all domains to database
    bps_api.all_domains()

    # Get and store all subjects to database
    bps_api.all_subjects()

    # Get and store all variables to database
    bps_api.all_variables()


if __name__ == "__main__":
    main()
