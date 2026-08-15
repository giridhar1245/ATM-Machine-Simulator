# ATM Machine Simulator

## Project Description

ATM Machine Simulator is a Python-based console application that simulates common ATM banking operations. The project provides a simple and interactive menu-driven system for account authentication, balance enquiry, cash withdrawal, cash deposit, PIN change, transaction history, and ATM cash status.

## Features

- Account number and PIN authentication
- Account locking after 3 incorrect PIN attempts
- Balance enquiry
- Cash withdrawal
- Cash deposit
- PIN change
- Transaction history
- ATM cash availability status
- Daily withdrawal limit
- Per-transaction withdrawal limit
- Withdrawal transaction fee
- Session timeout
- Transaction receipts
- Input validation
- Multiple demo accounts

## Technologies Used

- Python
- Object-Oriented Programming (OOP)
- `datetime`
- `time`
- `re`
- Python type hints

## Project Structure

```text
ATM-Machine-Simulator
│
├── atm_machine.py
└── README.md
```

## Demo Accounts

| Account Number | PIN  | Account Holder | Initial Balance |
|---|---:|---|---:|
| 1234567890 | 1234 | John Doe | ₹15,000 |
| 0987654321 | 5678 | Jane Smith | ₹25,000 |
| 1122334455 | 9012 | Bob Johnson | ₹5,000 |
| 5544332211 | 3456 | Alice Brown | ₹75,000 |

> These are demo accounts for testing only. They are not real banking credentials.

## ATM Operations

### 1. Balance Enquiry
Displays the current account balance and creates a transaction record.

### 2. Cash Withdrawal
Allows withdrawal subject to:
- Available account balance
- ₹25,000 per-transaction limit
- ₹50,000 daily withdrawal limit
- ATM cash availability
- Valid withdrawal denominations

### 3. Cash Deposit
Allows deposits up to ₹1,000,000 per transaction and validates the amount.

### 4. Change PIN
Allows the user to change the current 4-digit PIN after verification.

### 5. Transaction History
Displays recent transactions with transaction ID, date, type, amount, balance, and status.

### 6. ATM Cash Status
Displays available cash in the ATM and indicates whether the cash level is normal or low.

## Security Features

- PIN verification
- Maximum of 3 failed PIN attempts
- Account locking after failed attempts
- Session timeout after inactivity
- Input validation
- Demo credentials only

## Project Description

**ATM Machine Simulator:** Developed a Python-based ATM simulation system using Object-Oriented Programming. Implemented PIN authentication, account locking, balance enquiry, cash withdrawal, cash deposit, PIN change, transaction history, transaction fees, daily withdrawal limits, session timeout, and input validation.

## Author

**Giridhar**

GitHub: https://github.com/giridhar1245
