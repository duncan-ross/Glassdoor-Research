import requests
from definitions import GLASSDOOR_API_HOST_URL, DEFAULT_HEADERS

LOCAL_IP = "192.168.0.50"

# Finds and returns the associated Glassdoor URL for the name provided
def get_company(name):
    results = employers(name)

    if not results or not results.get("employers"):
        return None

    return results["employers"][0]


# Searches for companies on Glassdoor that meet the query specification
def employers(query):
    payload = base_payload()

    payload["action"] = "employers"
    payload["q"] = query

    return json_request(payload)


# Sends the json request to Glassdoor with the specified payload and headers
def json_request(payload):
    try:
        r = requests.get(
            GLASSDOOR_API_HOST_URL, params=payload, headers=DEFAULT_HEADERS
        )
    except (requests.exceptions.RequestException, e):
        return {"error": e.message}

    try:
        json_response = r.json()
    except ValueError:
        return {"error": "No JSON response"}

    if json_response.get("status") != "OK":
        return {"status": json_response.get("status")}

    return json_response.get("response")


def base_payload():
    return {
        "v": "1",
        "format": "json",
        "t.p": "GLASSDOOR_PARTNER_ID",  # config('GLASSDOOR_PARTNER_ID'),
        "t.k": "GLASSDOOR_PARTNER_KEY",  # config('GLASSDOOR_PARTNER_KEY'),
        "userip": LOCAL_IP,
        "country": "us",
    }
