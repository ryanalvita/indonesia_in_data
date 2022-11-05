# Get and store all data from BPS Web API

import json
import os
import requests
from pymongo import MongoClient


def all_variables():
    # Initialize MongoDB
    client = MongoClient(os.environ["MONGODB_URI"])
    database = client["bps_database"]

    # Get all domains from database
    collection = database["domains"]
    domains = list(collection.find({}))

    # Get all variables from BPS API for each domain
    # Create collection
    collection = database["variables"]
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
    all_variables()


if __name__ == "__main__":
    main()
