@echo off
REM SmartBetslip API Quick Test Script (Windows PowerShell/CMD)
REM =========================================================
REM
REM This script provides quick curl commands to test the SmartBetslip API integration.
REM Requires curl to be installed and available in PATH.
REM
REM SmartBetslip Client: Enterprise Flat Rate ($2,500/month)
REM API Key: pk_bAfM0... (1000 requests/minute)
REM

set BASE_URL=http://localhost:8000
set API_KEY=pk_bAfM0swfeiwU8yrEHNzMphlRnZ7R9FmUZOaDtLG370o

echo.
echo ========================================
echo SmartBetslip API Quick Test Suite
echo ========================================
echo Base URL: %BASE_URL%
echo API Key: %API_KEY:~0,20%...
echo.

echo [1/6] Testing Authentication - Get Balance
curl -X GET "%BASE_URL%/api/v1/balance" ^
     -H "Authorization: Bearer %API_KEY%" ^
     -H "Content-Type: application/json" ^
     -w "\nStatus: %%{http_code}\n" -s
echo.

echo [2/6] Testing Betslip Generation
curl -X POST "%BASE_URL%/api/v1/betslip/generate" ^
     -H "Authorization: Bearer %API_KEY%" ^
     -H "Content-Type: application/json" ^
     -d "{\"user_id\":\"test_user_123\",\"bets\":[{\"event_id\":\"nfl_001\",\"market\":\"moneyline\",\"selection\":\"Patriots -3.5\",\"odds\":1.91,\"stake\":100.00}],\"total_stake\":100.00,\"currency\":\"USD\",\"betting_type\":\"single\"}" ^
     -w "\nStatus: %%{http_code}\n" -s
echo.

echo [3/6] Testing Payment Creation
curl -X POST "%BASE_URL%/api/v1/payments" ^
     -H "Authorization: Bearer %API_KEY%" ^
     -H "Content-Type: application/json" ^
     -d "{\"amount\":500.00,\"currency\":\"USD\",\"payment_method\":\"crypto\",\"crypto_currency\":\"USDT_TRC20\",\"description\":\"SmartBetslip deposit\"}" ^
     -w "\nStatus: %%{http_code}\n" -s
echo.

echo [4/6] Testing Withdrawal Creation
curl -X POST "%BASE_URL%/api/v1/withdrawals" ^
     -H "Authorization: Bearer %API_KEY%" ^
     -H "Content-Type: application/json" ^
     -d "{\"amount\":250.00,\"currency\":\"USD\",\"withdrawal_method\":\"crypto\",\"crypto_currency\":\"USDT_TRC20\",\"wallet_address\":\"TQn9Y2khEsLJW1ChVWFMSMeRDow5KcbLSE\",\"description\":\"SmartBetslip withdrawal\"}" ^
     -w "\nStatus: %%{http_code}\n" -s
echo.

echo [5/6] Testing Payments List
curl -X GET "%BASE_URL%/api/v1/payments" ^
     -H "Authorization: Bearer %API_KEY%" ^
     -H "Content-Type: application/json" ^
     -w "\nStatus: %%{http_code}\n" -s
echo.

echo [6/6] Testing Invalid Authentication
curl -X GET "%BASE_URL%/api/v1/balance" ^
     -H "Authorization: Bearer invalid_key" ^
     -H "Content-Type: application/json" ^
     -w "\nStatus: %%{http_code} (should be 401)\n" -s
echo.

echo ========================================
echo SmartBetslip API Test Complete
echo ========================================
echo.
echo Expected Results:
echo - Balance: Status 200 with balance data
echo - Betslip: Status 201 with betslip_id
echo - Payment: Status 201 with payment_id
echo - Withdrawal: Status 201 with withdrawal_id
echo - Payments List: Status 200 with payments array
echo - Invalid Auth: Status 401 (Unauthorized)
echo.
pause
