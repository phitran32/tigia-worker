import pyodbc
from decimal import Decimal
from datetime import datetime


class SQLManager:
    def __init__(self, server_name, database_name, username, password):
        self.server_name = server_name
        self.database_name = database_name
        self.username = username
        self.password = password
        self.conn = None

    def connect(self):
        """Kết nối đến SQL Server."""
        connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.server_name};DATABASE={self.database_name};UID={self.username};PWD={self.password}"
        self.conn = pyodbc.connect(connection_string)
        return self.conn

    def close(self):
        """Đóng kết nối."""
        if self.conn:
            self.conn.close()
            self.conn = None


    def update_tigia(self, currency_code, currency_name, buy, transfer, sell):
        """Cập nhật tỷ giá vào database."""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            print("👉 Debug SQL params:", currency_code, currency_name, buy, transfer, sell)
            # Gọi stored procedure với 5 tham số
            cursor.execute(
                "{CALL SP_INSERT_THONGTINTIGIA (?, ?, ?, ?, ?)}",
                (currency_code, currency_name, buy, transfer, sell)
            )
            print("✅ SP executed, Rows affected:", cursor.rowcount)
            result = cursor.fetchall()  # lấy dữ liệu SELECT trả về
            for row in result:
                print("👉 SP result:", row)

            conn.commit()
            print(f"✅ Đã chèn tỷ giá {currency_code} vào DB")

        except Exception as e:
            print(f"❌ Lỗi khi cập nhật tỷ giá {currency_code}: {e}")
        finally:
            try:
                cursor.close()
                self.close()
            except:
                pass