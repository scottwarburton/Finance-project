
import requests
from bs4 import BeautifulSoup

url = "https://finance.yahoo.com/quote/GOOG"
headers = {'User-Agent': 'Mozilla/5.0'}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, "lxml")
range = soup.find("div", {"data-test": "left-summary-table"}).find("table").find("tbody").find_all("tr")[5].find_all("td")[
        1].text
low52 = float(range.split("-")[0].rstrip().replace(",", ""))
high52 = float(range.split("-")[1].lstrip().replace(",", ""))

print(range.split("-"))
print(low52)
print(high52)

"""
table data
<div class="D(ib) W(1/2) Bxz(bb) Pstart(12px) Va(t) ie-7_D(i) ie-7_Pos(a) smartphone_D(b) smartphone_W(100%) smartphone_Pstart(0px) smartphone_BdB smartphone_Bdc($seperatorColor)" data-test="right-summary-table">
    <table class="W(100%) M(0) Bdcl(c)">
        <tbody>
            <tr class="Bxz(bb) Bdbw(1px) Bdbs(s) Bdc($seperatorColor) H(36px) ">
                <td class="C($primaryColor) W(51%)">
                    <span>Market Cap</span>
                </td>
                <td class="Ta(end) Fw(600) Lh(14px)" data-test="MARKET_CAP-value">
                    <span class="Trsdu(0.3s) ">2.498T</span>
                </td>
            </tr>
            <tr class="Bxz(bb) Bdbw(1px) Bdbs(s) Bdc($seperatorColor) H(36px) ">
                <td class="C($primaryColor) W(51%)">
                    <span>Beta (5Y Monthly)</span>
                </td>
                <td class="Ta(end) Fw(600) Lh(14px)" data-test="BETA_5Y-value">
                    <span class="Trsdu(0.3s) ">1.20</span>
                </td>
            </tr>
            <tr class="Bxz(bb) Bdbw(1px) Bdbs(s) Bdc($seperatorColor) H(36px) ">
                <td class="C($primaryColor) W(51%)">
                    <span>PE Ratio (TTM)</span>
                </td>
                <td class="Ta(end) Fw(600) Lh(14px)" data-test="PE_RATIO-value">
                    <span class="Trsdu(0.3s) ">29.58</span>
                </td>
            </tr>
            <tr class="Bxz(bb) Bdbw(1px) Bdbs(s) Bdc($seperatorColor) H(36px) ">
                <td class="C($primaryColor) W(51%)">
                    <span>EPS (TTM)</span>
                </td>
                <td class="Ta(end) Fw(600) Lh(14px)" data-test="EPS_RATIO-value">
                    <span class="Trsdu(0.3s) ">5.11</span>
                </td>
            </tr>
"""