import requests

ip = requests.get('https://api.ipify.org').text

def get_location_from_ip(ip):
    response = requests.get(f"https://ipinfo.io/{ip}/json")
    data = response.json()
    return {
        'city': data.get('city'),
        'region': data.get('region'),
        'country': data.get('country'),
        'loc': data.get('loc'),  # comma-separated lat/lon
    }
location= get_location_from_ip(ip)
# print(location)
# print(f"https://www.google.com/maps?q={location['loc']}")
