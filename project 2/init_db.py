import oracledb

db_config = {
    "user": "zehra",
    "password": "12345",
    "dsn": "localhost:1521/ORCL1"
}


def setup_database():
    try:
        connection = oracledb.connect(**db_config)
        cursor = connection.cursor()

        print("Oracle bazasına qoşuldu. Köhnə cədvəllər təmizlənir...")


        try:
            cursor.execute("DROP TABLE transactions CASCADE CONSTRAINTS")
        except Exception:
            pass
        try:
            cursor.execute("DROP TABLE users CASCADE CONSTRAINTS")
        except Exception:
            pass
        try:
            cursor.execute("DROP TABLE currencies CASCADE CONSTRAINTS")
        except Exception:
            pass

        print("\nYeni təhlükəsizlik dəstəkli cədvəllər yaradılır...")


        cursor.execute("""
            CREATE TABLE currencies (
                currency_code VARCHAR2(3) PRIMARY KEY,
                currency_name VARCHAR2(20) NOT NULL,
                symbol VARCHAR2(5)
            )
        """)


        cursor.execute("""
            CREATE TABLE users (
                user_id VARCHAR2(50) PRIMARY KEY,
                username VARCHAR2(30) NOT NULL UNIQUE, 
                password_hash VARCHAR2(100) NOT NULL, -- Şifrələnmiş formada saxlanacaq
                full_name VARCHAR2(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("- 'users' (İstifadəçilər) cədvəli yaradıldı.")


        cursor.execute("""
            CREATE TABLE transactions (
                transaction_id VARCHAR2(50) PRIMARY KEY,
                user_id VARCHAR2(50), -- Ödənişi edən istifadəçi
                amount NUMBER(10, 2) NOT NULL,
                currency_code VARCHAR2(3) NOT NULL,
                azn_equivalent NUMBER(10, 2) NOT NULL,
                status VARCHAR2(20) DEFAULT 'SUCCESS',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_currency FOREIGN KEY (currency_code) REFERENCES currencies(currency_code),
                CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        print("- 'transactions' cədvəli istifadəçi əlaqəsi ilə yaradıldı.")


        insert_query = "INSERT INTO currencies (currency_code, currency_name, symbol) VALUES (:1, :2, :3)"
        cursor.executemany(insert_query, [
            ("AZN", "Manat", "₼"),
            ("USD", "Dollar", "$"),
            ("EUR", "Avro", "€")
        ])

        connection.commit()
        print("\n[UĞURLU] Baza qeydiyyat sistemi üçün tam sıfırlandı və hazırlandı!")

    except Exception as e:
        print(f"\nXəta: {e}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'connection' in locals(): connection.close()


if __name__ == "__main__":
    setup_database()