# Get and store all domains basedata from BPS Web API

import json
import os
import requests
from pymongo import MongoClient


def all_domains():
    # Initialize MongoDB
    client = MongoClient(os.environ["MONGODB_URI"])
    database = client["bps_database"]

    # Get all domains from BPS API
    params = {"type": "all", "key": os.environ["BPS_API_KEY"]}
    response = requests.get(url="https://webapi.bps.go.id/v1/api/domain", params=params)
    domains = json.loads(response.text)["data"][1]

    # Store to database
    collection = database["domains"]
    for domain in domains:
        domain_id = domain["domain_id"]
        # Define filters based on domain_id
        filter = {"domain_id": f"{domain_id}"}

        # Determine values to be updated
        values = {"$set": domain}

        # Update values to database
        collection.update_one(filter=filter, update=values, upsert=True)


def main():
    all_domains()


if __name__ == "__main__":
    main()
