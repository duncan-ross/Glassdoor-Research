import requests
LOCAL_IP = "192.168.0.50"
GLASSDOOR_API_HOST_URL = 'http://api.glassdoor.com/api/api.htm'
GLASSDOOR_PARTNER_ID = '157426'
GLASSDOOR_PARTNER_KEY = 'iDIHGVDrCcA'

def base_payload(action, query):
  return {
  'v': '1',
  'format': 'json',
  't.p':  GLASSDOOR_PARTNER_ID,
  't.k':  GLASSDOOR_PARTNER_KEY,
  'userip': LOCAL_IP,
  'country': 'us',
  'action': action,
  'q': query,
}

headers = {'User-Agent': 'Mozilla/5.0'}
payload = base_payload('employers', 'Google')
r = requests.get(GLASSDOOR_API_HOST_URL, params=payload, headers=headers)

json_response = r.json()
response = json_response.get('response')
print(response)