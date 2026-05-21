import oracledb
import uuid
import hashlib
import re
from fastapi import HTTPException
from pydantic import BaseModel

class RegisterInput(BaseModel):
    username: str
    password: str
    full_name: str

class LoginInput(BaseModel):
    username: str
    password: str

class AuthService:
    def __init__(self, db_config):
        self.db_config = db_config

    def _validate_password(self, password: str):
        if len(password) < 8: return "Şifrə ən azı 8 simvoldan ibarət olmalıdır!"
        if not re.search("[a-z]", password): return "Şifrədə ən azı bir kiçik hərf (a-z) olmalıdır!"
        if not re.search("[A-Z]", password): return "Şifrədə ən azı bir böyük hərf (A-Z) olmalıdır!"
        if not re.search("[0-9]", password): return "Şifrədə ən azı bir rəqəm (0-9) olmalıdır!"
        if not re.search("[_@$!%*?&.#-]", password): return "Şifrədə ən azı bir xüsusi simvol olmalıdır!"
        return None

    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, data: RegisterInput):
        error = self._validate_password(data.password)
        if error: raise HTTPException(status_code=400, detail=error)

        hashed_pwd = self._hash_password(data.password)
        generated_user_id = f"usr_{uuid.uuid4().hex[:8]}"

        try:
            connection = oracledb.connect(**self.db_config)
            cursor = connection.cursor()
            sql = "INSERT INTO users (user_id, username, password_hash, full_name) VALUES (:1, :2, :3, :4)"
            cursor.execute(sql, (generated_user_id, data.username.lower().strip(), hashed_pwd, data.full_name))
            connection.commit()
            return {"status": "SUCCESS", "user_id": generated_user_id, "message": f"Təbrik edirik {data.full_name}, qeydiyyat uğurludur!"}
        except oracledb.IntegrityError:
            raise HTTPException(status_code=400, detail="Bu istifadəçi adı artıq götürülüb!")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'connection' in locals(): connection.close()

    def login(self, data: LoginInput):
        username_clean = data.username.lower().strip()
        try:
            connection = oracledb.connect(**self.db_config)
            cursor = connection.cursor()
            cursor.execute("SELECT user_id, password_hash, full_name FROM users WHERE username = :1", (username_clean,))
            user_row = cursor.fetchone()

            if not user_row:
                raise HTTPException(status_code=404, detail="Belə bir istifadəçi mövcud deyil!")

            if self._hash_password(data.password) != user_row[1]:
                raise HTTPException(status_code=401, detail="Daxil etdiyiniz şifrə yanlışdır!")

            return {"status": "WELCOME", "user_id": user_row[0], "full_name": user_row[2], "message": "Uğurla giriş etdiniz."}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'connection' in locals(): connection.close()