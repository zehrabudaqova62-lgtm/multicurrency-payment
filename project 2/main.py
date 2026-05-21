from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles # Statik fayllar üçün əlavə olundu
import os

from auth_service import AuthService, RegisterInput, LoginInput
from payment_service import PaymentService, PaymentInput

app = FastAPI(
    title="Matrix Multi-Currency Payment Gateway",
    description="Real zamanlı məzənnə konvertasiyası.",
    version="4.0"
)

db_config = {
    "user": "zehra",
    "password": "12345",
    "dsn": "localhost:1521/ORCL1"
}

auth_service = AuthService(db_config)
payment_service = PaymentService(db_config)


current_dir = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(current_dir, "templates")


app.mount("/static", StaticFiles(directory=templates_dir), name="static")


@app.get("/", response_class=HTMLResponse, tags=["Veb İnterfeys"])
def read_root():
    html_path = os.path.join(templates_dir, "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)


@app.post("/api/v1/auth/register", tags=["İstifadəçi Təhlükəsizliyi"])
def register(data: RegisterInput):
    return auth_service.register(data)

@app.post("/api/v1/auth/login", tags=["İstifadəçi Təhlükəsizliyi"])
def login(data: LoginInput):
    return auth_service.login(data)

@app.post("/api/v1/pay", tags=["Ödəniş Əməliyyatları"])
def pay(data: PaymentInput):
    return payment_service.process_payment(data)

@app.get("/api/v1/reports", tags=["Maliyyə Hesabatları"])
def reports():
    return payment_service.get_reports()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)