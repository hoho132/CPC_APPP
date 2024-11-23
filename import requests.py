
import requests

web_app_url = "https://script.google.com/macros/s/AKfycbxz-guGHcedl2bpaw_XfnvSx2i_alQyPmTadLM6NuY9j9AxXd0llnImOjOkPIJhbD0y/exec"  # Replace with your Web App URL
qr_code = "IEYhz/+agJrmyvJstsvSKwMLBMrVx0hilsRSnWfu48E="  # Test QR code

data = {"qr_code": qr_code}
response = requests.post(web_app_url, json=data)

print("Status Code:", response.status_code)

# Safely print the response text

