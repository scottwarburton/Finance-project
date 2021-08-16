
import requests
from bs4 import BeautifulSoup

url = "https://finance.yahoo.com/quote/AAPL"
headers = {'User-Agent': 'Mozilla/5.0'}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, "lxml")
stock_price = soup.find_all("span", {"class": "Trsdu(0.3s)"})
print(stock_price)