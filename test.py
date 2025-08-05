import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://api.pluggy.ai/auth"
payload = {
    "clientId": "-",
    "clientSecret": "-"
}

try:
    response = requests.post(url, json=payload, verify=False)
    response.raise_for_status()
    print("Autenticado com sucesso!")
    print(response.json())
except requests.exceptions.RequestException as e:
    print("Erro:", e)
