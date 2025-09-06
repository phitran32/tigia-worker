import schedule
import time
from decimal import Decimal
import requests
import xml.etree.ElementTree as ET
from SQLManager import SQLManager
import os

sql_manager = SQLManager(
    server_name = "14.161.14.133",
    database_name = "QuanLyKhoMoc2023",
    username = "sa",
    password = "9905376"
)


# sql_manager = SQLManager(
#     server_name   = os.getenv("DB_SERVER"),
#     database_name = os.getenv("DB_NAME"),
#     username      = os.getenv("DB_USER"),
#     password      = os.getenv("DB_PASS")
# )


def get_vcb_rates():
    url = "https://portal.vietcombank.com.vn/Usercontrols/TVPortal.TyGia/pXML.aspx?b=10"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    # Gửi yêu cầu GET
    res = requests.get(url, headers=headers, timeout=10)
    res.encoding = 'utf-8'
    xml_text = res.text

    # Phân tích XML
    root = ET.fromstring(xml_text)
    rates = {}
    for ex in root.findall('Exrate'):
        code = ex.attrib.get('CurrencyCode')
        buy = ex.attrib.get('Buy')
        transfer = ex.attrib.get('Transfer')
        sell = ex.attrib.get('Sell')
        rates[code] = {
            "Buy": buy,
            "Transfer": transfer,
            "Sell": sell
        }
    return rates

# if __name__ == "__main__":
#     try:
#         data = get_vcb_rates()
#         for curr, vals in data.items():
#             print(curr, vals)
#     except Exception as e:
#         print("Lỗi khi lấy hoặc phân tích dữ liệu:", e)


def get_usd_rate():
    url = "https://portal.vietcombank.com.vn/Usercontrols/TVPortal.TyGia/pXML.aspx?b=10"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers, timeout=10)
    res.encoding = "utf-8"

    root = ET.fromstring(res.text)
    for ex in root.findall("Exrate"):
        if ex.attrib.get("CurrencyCode", "").strip() == "USD":
            # loại dấu phẩy và chuyển sang Decimal
            def D(x): return Decimal(x.replace(",", "")).quantize(Decimal("0.01"))
            return {
                "CurrencyCode": ex.attrib.get("CurrencyCode", "").strip(),
                "CurrencyName": ex.attrib.get("CurrencyName", "").strip(),
                "Buy": D(ex.attrib.get("Buy", "0")),
                "Transfer": D(ex.attrib.get("Transfer", "0")),
                "Sell": D(ex.attrib.get("Sell", "0")),
            }
    return None

# Hàm chính
def job():
    print("🔍 Đang thực hiện công việc...")
    usd = get_usd_rate()
    if usd:
        print("💵 Tỷ giá USD/VND (Vietcombank):")
        print(f"  CurrencyCode     : {usd['CurrencyCode']}")
        print(f"  CurrencyName     : {usd['CurrencyName']}")
        print(f"  Mua tiền mặt     : {usd['Buy']}")
        print(f"  Mua chuyển khoản : {usd['Transfer']}")
        print(f"  Bán ra           : {usd['Sell']}")
        sql_manager.update_tigia(
            usd["CurrencyCode"],
            usd["CurrencyName"],
            usd["Buy"],
            usd["Transfer"],
            usd["Sell"]
        )
    else:
        print("❌ Không tìm thấy tỷ giá USD")


if __name__ == "__main__":
    try:
        job()
    except Exception as e:
        print("Lỗi khi chạy job:", e)

# Lên lịch chạy mỗi 1 phút
# schedule.every(2).minutes.do(job)

# # Chạy chương trình
# print("⏰ Bắt đầu chụp màn hình và gửi email tự động. Nhấn Ctrl+C để dừng.")
# while True:
#     schedule.run_pending()
#     time.sleep(1)