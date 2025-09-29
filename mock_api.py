# mock_api.py (FastAPI version)
import random

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


# Pydantic models for request body validation
class User(BaseModel):
    name: str
    email: str


class Account(BaseModel):
    user_id: int
    currency: str


class Transaction(BaseModel):
    account_id: int
    amount: float


class Analytics(BaseModel):
    user_id: int
    account_id: int
    pattern: str = None


app = FastAPI()

# In-memory data stores or db
db = {
    "users": {},
    "accounts": {},
    "transactions": [],
    "analytics": []
}

# Simple auto-incrementing IDs
next_user_id = 1
next_account_id = 1


@app.post("/users", status_code=201)
def create_user(user: User):
    global next_user_id
    if '@' not in user.email:
        raise HTTPException(status_code=400, detail="Invalid user data")

    user_id = next_user_id
    db["users"][user_id] = user.model_dump()
    print(db["users"])
    response_data = db["users"][user_id]
    response_data['user_id'] = user_id

    next_user_id += 1
    return response_data


@app.post("/accounts", status_code=201)
def create_account(account: Account):
    global next_account_id
    user_id = account.user_id

    if user_id not in db["users"]:
        raise HTTPException(status_code=404, detail=f"User with user_id {user_id} not found")

    account_id = next_account_id
    db["accounts"][account_id] = account.model_dump()

    response_data = db["accounts"][account_id]
    response_data['account_id'] = account_id

    next_account_id += 1
    return response_data


@app.post("/transactions", status_code=201)
def create_transaction(transaction: Transaction) -> dict:
    account_id = transaction.account_id
    amount = transaction.amount

    if account_id not in db["accounts"]:
        raise HTTPException(status_code=404, detail=f"Account with account_id {account_id} not found")

    if amount <= 0:
        raise HTTPException(status_code=400, detail="Transaction amount must be positive")

    db["transactions"].append(transaction.model_dump())
    return {"message": "Transaction successful"}


# write an api to create analytics from user_id and account_id
@app.post("/analytics")
def analytics(analytics: Analytics) -> Analytics:
    if analytics.user_id not in db["users"]:
        raise HTTPException(status_code=404, detail=f"User with user_id {analytics.user_id} not found")
    if analytics.account_id not in db["accounts"]:
        raise HTTPException(status_code=404, detail=f"Account with account_id {analytics.account_id} not found")

    # mock for user behavior code in platform usage
    pattern_types = ["A", "B", "C", "D", "E", "F"]

    analytics.pattern = random.choice(pattern_types)
    db["analytics"].append(analytics.model_dump())
    return analytics


# Optional: Add a root endpoint for easy verification
@app.get("/")
def read_root():
    return {"message": "FastAPI Mock Server is running"}


if __name__ == "__main__":
    uvicorn.run("mock_api:app", host="127.0.0.1", port=8000, reload=True)
