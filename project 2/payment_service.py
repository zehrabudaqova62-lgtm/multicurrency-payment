import oracledb
import uuid
from fastapi import HTTPException
from pydantic import BaseModel

class PaymentInput(BaseModel):
    user_id: str
    amount: float
    currency: str

class PaymentService:
    def __init__(self, db_config):
        self.db_config = db_config
        self.EXCHANGE_RATES = {"AZN": 1.0, "USD": 1.70, "EUR": 1.85}

    def process_payment(self, data: PaymentInput):
        currency_upper = data.currency.upper()
        if currency_upper not in self.EXCHANGE_RATES:
            raise HTTPException(status_code=400, detail="Yalnız AZN, USD və EUR dəstəklənir.")
        if data.amount <= 0:
            raise HTTPException(status_code=400, detail="Məbləğ 0-dan böyük olmalıdır.")

        rate = self.EXCHANGE_RATES[currency_upper]
        calculated_azn = data.amount * rate
        generated_id = f"txn_{uuid.uuid4().hex[:10]}"

        try:
            connection = oracledb.connect(**self.db_config)
            cursor = connection.cursor()

            cursor.execute("SELECT username FROM users WHERE user_id = :1", (data.user_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Ödəniş etmək istəyən istifadəçi tapılmadı!")

            sql = "INSERT INTO transactions (transaction_id, user_id, amount, currency_code, azn_equivalent) VALUES (:1, :2, :3, :4, :5)"
            cursor.execute(sql, (generated_id, data.user_id, data.amount, currency_upper, calculated_azn))
            connection.commit()

            return {"status": "APPROVED", "transaction_id": generated_id, "converted_to_azn": f"{calculated_azn:.2f} AZN", "message": "Ödəniş qəbul edildi."}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'connection' in locals(): connection.close()

    def get_reports(self):
        try:
            connection = oracledb.connect(**self.db_config)
            cursor = connection.cursor()
            query = """
                SELECT t.transaction_id, u.username, t.amount, t.currency_code, t.azn_equivalent, t.created_at 
                FROM transactions t
                JOIN users u ON t.user_id = u.user_id
                ORDER BY t.created_at DESC
            """
            cursor.execute(query)
            rows = cursor.fetchall()

            report_list = []
            for row in rows:
                report_list.append({
                    "transaction_id": row[0],
                    "customer_username": row[1],
                    "amount": row[2],
                    "currency": row[3],
                    "azn_equivalent": row[4],
                    "date": str(row[5])
                })
            return {"total_payments_count": len(report_list), "transactions": report_list}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'connection' in locals(): connection.close()