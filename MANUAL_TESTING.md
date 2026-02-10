# Manual Verification Guide

Use this guide to demonstrate the platform to friends or for your own verification.

## Prerequisites
Ensure the system is running:
- Backend: `uvicorn app.main:app` (Port 8000)
- Frontend: `npm run dev` (Port 5173)
- Database/Redis: `docker compose up`

## Demo Walkthrough

### 1. User Registration & Login
1.  Open [http://localhost:5173](http://localhost:5173).
2.  Click **Register**.
3.  Enter Email: `demo@example.com`, Password: `password123`.
4.  Click **Register**. You should be redirected to Login.
5.  Login with the same credentials.
6.  *Observation*: You'll see the Dashboard with a **Balance** of $100,000.

### 2. View Real-Time Market
1.  The dashboard shows a Ticker in the header (e.g., `AAPL: $150.00`) updating live.
    - *Note*: This data is powered by a background simulation task and streamed via WebSockets.

### 3. Place a Limit Buy Order
1.  In the **Order Form**:
    - **Symbol**: `AAPL` (or whatever is simulated)
    - **Type**: `LIMIT`
    - **Side**: `BUY`
    - **Quantity**: `10`
    - **Price**: `$140.00` (Below market price)
2.  Click **Submit Order**.
3.  *Observation*: 
    - The order appears in the **Order Book** under "Bids" (Green side).
    - Your **Available Balance** decreases (funds locked).

### 4. Execute a Trade (Match)
1.  Open a **New Incognito Window** (simulating a second user).
2.  Register/Login as `seller@example.com`.
3.  In the Order Form:
    - **Symbol**: `AAPL`
    - **Type**: `LIMIT`
    - **Side**: `SELL`
    - **Quantity**: `10`
    - **Price**: `$140.00` (Matching your buy order)
4.  Click **Submit Order**.
5.  *Observation*:
    - The order disappears from the book (Matched!).
    - A **Trade Notification** or update appears (via WebSocket).
    - The Seller's balance increases.

### 5. Check Portfolio
1.  Switch back to `demo@example.com` window.
2.  Refresh/Check Holdings. You now own 10 AAPL.

## Troubleshooting
- If Order Book is empty, make sure Redis is running (`docker compose ps`).
- If orders fail, check console for specific errors (e.g., Insufficient Funds).
