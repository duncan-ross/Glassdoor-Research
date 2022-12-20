import requests
from helpers import local_ip, config
from definitions import GLASSDOOR_API_HOST_URL

#LOCAL_IP = local_ip()
LOCAL_IP = "192.168.0.50"

# Finds and returns the associated Glassdoor URL for the name provided
def get_company(name):
  results = employers(name)
  
  if not results or not results.get('employers'):
    return None
  
  return results['employers'][0]
  
# Searches for companies on Glassdoor that meet the query specification
def employers(query):
  payload = base_payload()
  
  payload['action'] = 'employers'
  payload['q'] = query
  
  return json_request(payload, base_headers())
  
# Sends the json request to Glassdoor with the specified payload and headers
def json_request(payload, headers):
  try:
    r = requests.get(GLASSDOOR_API_HOST_URL, params=payload, headers=headers)
  except (requests.exceptions.RequestException, e):
    return {'error': e.message}
  
  try:
    json_response = r.json()
  except ValueError:
    return {'error': 'No JSON response'}
  
  if json_response.get('status') != 'OK':
    return {'status': json_response.get('status')}

  
  return json_response.get('response')


def base_payload():
  return {
  'v': '1',
  'format': 'json',
  't.p':  '157426',  # config('GLASSDOOR_PARTNER_ID'),
  't.k':  'iDIHGVDrCcA', # config('GLASSDOOR_PARTNER_KEY'),
  'userip': LOCAL_IP,
  'country': 'us',
}


def base_headers():
  return {'User-Agent': 'Mozilla/5.0'}