
import requests
import json
import sys
import os

API_URL = "http://localhost:8000/api/v1"

def get_token():
    response = requests.post(f"{API_URL}/auth/login", data={"username": "admin", "password": "admin123"})
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        sys.exit(1)
    return response.json()["access_token"]

def main():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # 1. Get FlightBooking Request Type ID
    response = requests.get(f"{API_URL}/request-types/", headers=headers)
    if response.status_code != 200:
        print(f"Failed to list request types: {response.text}")
        sys.exit(1)
    
    rts = response.json()
    flight_booking = next((rt for rt in rts if rt["name"] == "FlightBooking"), None)
    
    if not flight_booking:
        print("FlightBooking request type not found!")
        sys.exit(1)
    
    rt_id = flight_booking["id"]
    print(f"Found FlightBooking ID: {rt_id}")

    # 2. Configure Parameters
    # Params: origin, destination, fromTime, toTime
    params_payload = {
        "is_active": True,
        "is_public": True,
        "max_items_per_request": 100,
        "available_indices": ["flights"],
        "parameters": [
            {
                "name": "origin",
                "description": "Origin City Code (e.g. THR)",
                "parameter_type": "string",
                "is_required": True,
                "placeholder_key": "origin",
                "validation_rules": {} 
            },
            {
                "name": "destination",
                "description": "Destination City Code (e.g. MHD)",
                "parameter_type": "string",
                "is_required": True,
                "placeholder_key": "destination",
                "validation_rules": {}
            },
            {
                "name": "fromTime",
                "description": "Departure Date (YYYY-MM-DD)",
                "parameter_type": "string",
                "is_required": False,
                "placeholder_key": "fromTime",
                "validation_rules": {}
            },
            {
                "name": "toTime",
                "description": "Return Date (YYYY-MM-DD)",
                "parameter_type": "string",
                "is_required": False,
                "placeholder_key": "toTime",
                "validation_rules": {}
            }
        ]
    }
    
    print("Configuring Parameters...")
    resp = requests.put(f"{API_URL}/request-types/{rt_id}/configure", headers=headers, json=params_payload)
    if resp.status_code != 200:
        print(f"Failed to configure params: {resp.text}")
    else:
        print("Parameters configured successfully.")

    # 3. Configure Query Template
    # Simple match query on origin/dest
    query_template = {
        "query": {
            "bool": {
                "must": [
                    {"match": {"origin": "{{origin}}"}},
                    {"match": {"destination": "{{destination}}"}}
                ]
            }
        }
    }
    
    # We need to wrap it in "elasticsearch_query_template" dict for the payload?
    # No, the model field is RequestTypeConfigureQuery.elasticsearch_query_template
    query_payload = {
        "elasticsearch_query_template": query_template
    }
    
    print("Configuring Query Template...")
    resp = requests.put(f"{API_URL}/request-types/{rt_id}/query", headers=headers, json=query_payload)
    if resp.status_code != 200:
        print(f"Failed to configure query: {resp.text}")
    else:
        print("Query template configured successfully.")

if __name__ == "__main__":
    main()
