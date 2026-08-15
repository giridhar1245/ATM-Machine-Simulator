import time
import re
from datetime import datetime
from typing import Optional, Dict, List, Tuple

class Transaction:
    def __init__(self, transaction_type: str, amount: float, balance_after: float, status: str):
        self.transaction_type = transaction_type
        self.amount = amount
        self.balance_after = balance_after
        self.status = status
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.transaction_id = f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}{id(self) % 1000:03d}"

    def __str__(self):
        return (f"ID: {self.transaction_id} | {self.timestamp} | "
                f"{self.transaction_type} | Amount: ₹{self.amount:.2f} | "
                f"Balance: ₹{self.balance_after:.2f} | Status: {self.status}")

class Account:
    def __init__(self, account_number: str, pin: str, initial_balance: float = 0.0, 
                 account_holder: str = "Customer"):
        self.account_number = account_number
        self._pin = pin
        self.balance = initial_balance
        self.account_holder = account_holder
        self.transaction_history: List[Transaction] = []
        self.max_withdrawal_limit = 25000.0
        self.daily_withdrawal_limit = 50000.0
        self.daily_withdrawn = 0.0
        self.last_reset_date = datetime.now().date()
        self.is_locked = False
        self.failed_attempts = 0
        self.max_failed_attempts = 3

    def verify_pin(self, pin: str) -> bool:
        if self.is_locked:
            return False

        if self._pin == pin:
            self.failed_attempts = 0
            return True
        else:
            self.failed_attempts += 1
            if self.failed_attempts >= self.max_failed_attempts:
                self.is_locked = True
            return False

    def change_pin(self, old_pin: str, new_pin: str) -> Tuple[bool, str]:
        if self.is_locked:
            return False, "Account is locked. Please contact customer service."

        if not self.verify_pin(old_pin):
            return False, "Incorrect current PIN."

        if len(new_pin) != 4 or not new_pin.isdigit():
            return False, "New PIN must be exactly 4 digits."

        if old_pin == new_pin:
            return False, "New PIN must be different from current PIN."

        self._pin = new_pin
        self.failed_attempts = 0
        return True, "PIN changed successfully."

    def check_balance(self) -> float:
        return self.balance

    def deposit(self, amount: float) -> Tuple[bool, str, float]:
        if self.is_locked:
            return False, "Account is locked. Please contact customer service.", self.balance

        if amount <= 0:
            return False, "Deposit amount must be greater than zero.", self.balance

        if amount > 1000000:
            return False, "Deposit amount exceeds maximum limit of ₹1,000,000.", self.balance

        if not self._validate_currency_notes(amount):
            return False, "Invalid currency denomination. Please use valid notes.", self.balance

        self.balance += amount
        transaction = Transaction("DEPOSIT", amount, self.balance, "COMPLETED")
        self.transaction_history.append(transaction)
        return True, f"Deposit successful. New balance: ₹{self.balance:.2f}", self.balance

    def withdraw(self, amount: float) -> Tuple[bool, str, float]:
        if self.is_locked:
            return False, "Account is locked. Please contact customer service.", self.balance

        if amount <= 0:
            return False, "Withdrawal amount must be greater than zero.", self.balance

        if amount > self.balance:
            return False, f"Insufficient balance. Available balance: ₹{self.balance:.2f}", self.balance

        if amount > self.max_withdrawal_limit:
            return False, f"Amount exceeds per-transaction limit of ₹{self.max_withdrawal_limit:.2f}", self.balance

        self._reset_daily_limit_if_needed()
        if self.daily_withdrawn + amount > self.daily_withdrawal_limit:
            return False, f"Daily withdrawal limit exceeded. Remaining limit: ₹{self.daily_withdrawal_limit - self.daily_withdrawn:.2f}", self.balance

        if not self._validate_withdrawal_amount(amount):
            return False, "Withdrawal amount must be in multiples of ₹100 or ₹500.", self.balance

        self.balance -= amount
        self.daily_withdrawn += amount
        transaction = Transaction("WITHDRAWAL", amount, self.balance, "COMPLETED")
        self.transaction_history.append(transaction)
        return True, f"Withdrawal successful. Please collect your cash: ₹{amount:.2f}. New balance: ₹{self.balance:.2f}", self.balance

    def _reset_daily_limit_if_needed(self):
        today = datetime.now().date()
        if self.last_reset_date != today:
            self.daily_withdrawn = 0.0
            self.last_reset_date = today

    def _validate_currency_notes(self, amount: float) -> bool:
        if amount % 10 != 0:
            return False
        return True

    def _validate_withdrawal_amount(self, amount: float) -> bool:
        if amount % 100 != 0 and amount % 500 != 0:
            return False
        return True

    def get_transaction_history(self, limit: int = 10) -> List[Transaction]:
        return self.transaction_history[-limit:]

    def __str__(self):
        return f"Account: {self.account_number} | Holder: {self.account_holder} | Balance: ₹{self.balance:.2f}"

class ATM:
    def __init__(self, atm_id: str = "ATM001", location: str = "Main Branch"):
        self.atm_id = atm_id
        self.location = location
        self.accounts: Dict[str, Account] = {}
        self.current_account: Optional[Account] = None
        self.is_authenticated = False
        self.cash_available = 500000.0
        self.min_cash_threshold = 50000.0
        self.session_timeout = 60
        self.last_activity = time.time()
        self.transaction_fees = {
            'balance_check': 0.0,
            'withdrawal': 5.0,
            'deposit': 0.0,
            'pin_change': 0.0
        }

    def add_account(self, account_number: str, pin: str, initial_balance: float = 0.0, 
                    account_holder: str = "Customer") -> bool:
        if account_number in self.accounts:
            return False

        self.accounts[account_number] = Account(account_number, pin, initial_balance, account_holder)
        return True

    def authenticate(self, account_number: str, pin: str) -> Tuple[bool, str]:
        if not account_number or not pin:
            return False, "Account number and PIN required."

        if account_number not in self.accounts:
            time.sleep(1)
            return False, "Invalid account number or PIN."

        account = self.accounts[account_number]

        if account.is_locked:
            return False, "Account is locked. Please contact customer service."

        if account.verify_pin(pin):
            self.current_account = account
            self.is_authenticated = True
            self.last_activity = time.time()
            return True, "Authentication successful."
        else:
            return False, f"Invalid PIN. {account.max_failed_attempts - account.failed_attempts} attempts remaining."

    def logout(self) -> None:
        self.current_account = None
        self.is_authenticated = False
        self.last_activity = time.time()

    def check_session(self) -> bool:
        if not self.is_authenticated or not self.current_account:
            return False

        if time.time() - self.last_activity > self.session_timeout:
            self.logout()
            return False

        self.last_activity = time.time()
        return True

    def get_balance(self) -> Optional[float]:
        if not self.check_session():
            return None

        transaction = Transaction("BALANCE_ENQUIRY", 0, self.current_account.balance, "COMPLETED")
        self.current_account.transaction_history.append(transaction)
        return self.current_account.balance

    def deposit(self, amount: float) -> Tuple[bool, str, Optional[float]]:
        if not self.check_session():
            return False, "Session expired. Please login again.", None

        if self.cash_available + amount > 10000000:
            return False, "ATM cash capacity exceeded. Cannot accept more deposits.", None

        success, message, new_balance = self.current_account.deposit(amount)
        if success:
            self.cash_available += amount
        return success, message, new_balance

    def withdraw(self, amount: float) -> Tuple[bool, str, Optional[float]]:
        if not self.check_session():
            return False, "Session expired. Please login again.", None

        if amount > self.cash_available:
            return False, f"Insufficient cash in ATM. Available: ₹{self.cash_available:.2f}", None

        success, message, new_balance = self.current_account.withdraw(amount)

        if success:
            fee = self.transaction_fees['withdrawal']
            if fee > 0:
                self.current_account.balance -= fee
                new_balance = self.current_account.balance
                fee_transaction = Transaction("WITHDRAWAL_FEE", fee, new_balance, "COMPLETED")
                self.current_account.transaction_history.append(fee_transaction)
                message += f" Withdrawal fee: ₹{fee:.2f} applied."

            self.cash_available -= amount

        return success, message, new_balance

    def change_pin(self, old_pin: str, new_pin: str) -> Tuple[bool, str]:
        if not self.check_session():
            return False, "Session expired. Please login again."

        return self.current_account.change_pin(old_pin, new_pin)

    def get_transaction_history(self, limit: int = 10) -> List[Transaction]:
        if not self.check_session():
            return []

        return self.current_account.get_transaction_history(limit)

    def check_cash_status(self) -> Dict[str, float]:
        return {
            'available': self.cash_available,
            'minimum_threshold': self.min_cash_threshold,
            'status': 'LOW' if self.cash_available < self.min_cash_threshold else 'NORMAL'
        }

class ATMInterface:
    def __init__(self, atm: ATM):
        self.atm = atm
        self.current_options = []

    def display_header(self, title: str = "ATM Service"):
        print("\n" + "=" * 50)
        print(f"  {title.center(46)}")
        print("=" * 50)

        if self.atm.is_authenticated and self.atm.current_account:
            account = self.atm.current_account
            print(f"  Account: {account.account_number}")
            print(f"  Holder: {account.account_holder}")
            if account.is_locked:
                print("  ⚠️ WARNING: Account is LOCKED")
        print("-" * 50)

    def display_menu(self, options: List[Tuple[str, str]]):
        print("\nAvailable Options:")
        print("-" * 40)
        for key, description in options:
            print(f"  {key}. {description}")
        print("-" * 40)
        print("  Q. Quit/Exit")
        print("-" * 40)

    def get_user_input(self, prompt: str, input_type: str = "string", 
                       validation_pattern: str = None) -> Optional[str]:
        while True:
            try:
                user_input = input(prompt).strip()

                if input_type == "string":
                    if user_input:
                        return user_input
                    else:
                        print("  Input cannot be empty. Please try again.")

                elif input_type == "number":
                    if user_input and user_input.replace('.', '').isdigit():
                        return user_input
                    else:
                        print("  Please enter a valid number.")

                elif input_type == "integer":
                    if user_input and user_input.isdigit():
                        return user_input
                    else:
                        print("  Please enter a valid integer.")

                elif input_type == "pin":
                    if user_input and user_input.isdigit() and len(user_input) == 4:
                        return user_input
                    else:
                        print("  PIN must be exactly 4 digits.")

                elif input_type == "money":
                    if user_input and user_input.replace('.', '').isdigit():
                        value = float(user_input)
                        if value > 0 and value % 10 == 0:
                            return user_input
                        else:
                            print("  Amount must be positive and in multiples of ₹10.")
                    else:
                        print("  Please enter a valid amount.")

                elif input_type == "amount_withdrawal":
                    if user_input and user_input.replace('.', '').isdigit():
                        value = float(user_input)
                        if value > 0 and (value % 100 == 0 or value % 500 == 0):
                            return user_input
                        else:
                            print("  Amount must be in multiples of ₹100 or ₹500.")
                    else:
                        print("  Please enter a valid amount.")

                elif input_type == "yes_no":
                    if user_input.lower() in ['y', 'yes', 'n', 'no']:
                        return user_input.lower()
                    else:
                        print("  Please enter 'Y' for yes or 'N' for no.")

                elif validation_pattern:
                    if re.match(validation_pattern, user_input):
                        return user_input
                    else:
                        print(f"  Input does not match required format.")

            except KeyboardInterrupt:
                print("\n\nOperation cancelled.")
                return None
            except Exception as e:
                print(f"  Error: {str(e)}. Please try again.")

    def show_welcome_screen(self):
        print("\n" + "=" * 50)
        print("  🏦 WELCOME TO THE ATM SYSTEM 🏦".center(50))
        print("=" * 50)
        print(f"  ATM ID: {self.atm.atm_id}")
        print(f"  Location: {self.atm.location}")
        print(f"  Date & Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        print("  💡 Please insert your card to begin")
        print("=" * 50)

    def show_loading_animation(self, duration: int = 1):
        for i in range(duration * 4):
            print(f"\r  Processing {'.' * (i % 4 + 1)}", end='')
            time.sleep(0.25)
        print("\r  ✓ Done!          ")

    def show_transaction_receipt(self, transaction_type: str, amount: float = 0, 
                                balance: float = 0, status: str = "COMPLETED"):
        print("\n" + "=" * 50)
        print("  RECEIPT".center(50))
        print("=" * 50)
        print(f"  ATM: {self.atm.atm_id}")
        print(f"  Account: {self.atm.current_account.account_number}")
        print(f"  Transaction: {transaction_type}")
        print(f"  Amount: ₹{amount:.2f}" if amount > 0 else "")
        print(f"  Balance: ₹{balance:.2f}")
        print(f"  Status: {status}")
        print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        print("  Thank you for using our ATM!".center(50))
        print("=" * 50)

    def show_account_locked_message(self):
        print("\n" + "!" * 50)
        print("  🔒 ACCOUNT LOCKED".center(50))
        print("!" * 50)
        print("  Your account has been locked due to multiple")
        print("  failed PIN attempts.")
        print("  Please contact customer service at 1-800-ATM-HELP")
        print("!" * 50)

    def show_session_expired_message(self):
        print("\n" + "!" * 50)
        print("  ⏰ SESSION EXPIRED".center(50))
        print("!" * 50)
        print("  Your session has expired due to inactivity.")
        print("  Please login again to continue.")
        print("!" * 50)

    def show_cash_status(self):
        cash_status = self.atm.check_cash_status()
        print("\n  ATM Cash Status:")
        print(f"  Available Cash: ₹{cash_status['available']:,.2f}")
        print(f"  Status: {'⚠️ LOW' if cash_status['status'] == 'LOW' else '✅ NORMAL'}")
        if cash_status['status'] == 'LOW':
            print("  ⚠️ Please contact bank for cash refill")

    def get_pin_input(self, prompt: str = "  Enter PIN: ") -> str:
        print(prompt, end='', flush=True)
        pin = input()
        return pin.strip()

    def run_transaction(self):
        while True:
            self.display_header("ATM Services")

            account = self.atm.current_account
            print(f"  Balance: ₹{account.balance:,.2f}")

            options = [
                ("1", "Balance Enquiry"),
                ("2", "Cash Withdrawal"),
                ("3", "Cash Deposit"),
                ("4", "Change PIN"),
                ("5", "Transaction History"),
                ("6", "Cash Status (ATM)"),
                ("7", "Logout & Exit")
            ]
            self.display_menu(options)

            choice = self.get_user_input("\n  Enter your choice: ", "string")

            if choice is None:
                continue

            if choice.lower() == 'q':
                print("\n  Thank you for using our ATM!")
                break

            if choice == "1":
                self.handle_balance_enquiry()
            elif choice == "2":
                self.handle_withdrawal()
            elif choice == "3":
                self.handle_deposit()
            elif choice == "4":
                self.handle_pin_change()
            elif choice == "5":
                self.handle_transaction_history()
            elif choice == "6":
                self.show_cash_status()
                input("\n  Press Enter to continue...")
            elif choice == "7":
                print("\n  Thank you for using our ATM!")
                self.atm.logout()
                break
            else:
                print("  Invalid choice. Please try again.")

            if not self.atm.check_session():
                self.show_session_expired_message()
                break

    def handle_balance_enquiry(self):
        self.display_header("Balance Enquiry")
        balance = self.atm.get_balance()

        if balance is not None:
            print(f"\n  💰 Current Balance: ₹{balance:,.2f}")
            print("\n  Transaction completed successfully.")
            self.show_transaction_receipt("BALANCE ENQUIRY", 0, balance)
        else:
            print("\n  ❌ Failed to retrieve balance.")

        input("\n  Press Enter to continue...")

    def handle_withdrawal(self):
        self.display_header("Cash Withdrawal")

        account = self.atm.current_account
        print(f"  Current Balance: ₹{account.balance:,.2f}")
        print(f"  Withdrawal Limit: ₹{account.max_withdrawal_limit:,.2f} per transaction")
        print(f"  Daily Limit: ₹{account.daily_withdrawal_limit:,.2f}")
        print(f"  Daily Used: ₹{account.daily_withdrawn:,.2f}")
        print(f"  Remaining Daily: ₹{account.daily_withdrawal_limit - account.daily_withdrawn:,.2f}")

        amount_input = self.get_user_input("\n  Enter withdrawal amount: ", "amount_withdrawal")
        if amount_input is None:
            return

        amount = float(amount_input)

        confirm = self.get_user_input(f"  Confirm withdrawal of ₹{amount:,.2f}? (Y/N): ", "yes_no")
        if confirm not in ['y', 'yes']:
            print("\n  Withdrawal cancelled.")
            input("  Press Enter to continue...")
            return

        success, message, new_balance = self.atm.withdraw(amount)

        if success:
            print(f"\n  ✅ {message}")
            self.show_transaction_receipt("WITHDRAWAL", amount, new_balance)
        else:
            print(f"\n  ❌ {message}")

        input("\n  Press Enter to continue...")

    def handle_deposit(self):
        self.display_header("Cash Deposit")

        account = self.atm.current_account
        print(f"  Current Balance: ₹{account.balance:,.2f}")

        amount_input = self.get_user_input("\n  Enter deposit amount: ", "money")
        if amount_input is None:
            return

        amount = float(amount_input)

        confirm = self.get_user_input(f"  Confirm deposit of ₹{amount:,.2f}? (Y/N): ", "yes_no")
        if confirm not in ['y', 'yes']:
            print("\n  Deposit cancelled.")
            input("  Press Enter to continue...")
            return

        success, message, new_balance = self.atm.deposit(amount)

        if success:
            print(f"\n  ✅ {message}")
            self.show_transaction_receipt("DEPOSIT", amount, new_balance)
        else:
            print(f"\n  ❌ {message}")

        input("\n  Press Enter to continue...")

    def handle_pin_change(self):
        self.display_header("Change PIN")

        old_pin = self.get_pin_input("  Enter current PIN: ")

        if not old_pin or len(old_pin) != 4 or not old_pin.isdigit():
            print("\n  ❌ Invalid PIN format.")
            input("  Press Enter to continue...")
            return

        print("\n  New PIN requirements:")
        print("  - Must be exactly 4 digits")
        print("  - Must be different from current PIN")

        new_pin = self.get_pin_input("  Enter new PIN: ")

        if not new_pin or len(new_pin) != 4 or not new_pin.isdigit():
            print("\n  ❌ Invalid PIN format.")
            input("  Press Enter to continue...")
            return

        confirm_pin = self.get_pin_input("  Confirm new PIN: ")

        if new_pin != confirm_pin:
            print("\n  ❌ PINs do not match.")
            input("  Press Enter to continue...")
            return

        success, message = self.atm.change_pin(old_pin, new_pin)

        if success:
            print(f"\n  ✅ {message}")
        else:
            print(f"\n  ❌ {message}")

        input("\n  Press Enter to continue...")

    def handle_transaction_history(self):
        self.display_header("Transaction History")

        limit_input = self.get_user_input("  Number of transactions to show (default 10): ", "string")
        limit = 10
        if limit_input and limit_input.isdigit():
            limit = min(int(limit_input), 50)

        transactions = self.atm.get_transaction_history(limit)

        if not transactions:
            print("\n  No transaction history available.")
        else:
            print(f"\n  Last {len(transactions)} Transactions:")
            print("-" * 80)
            print(f"  {'ID':<20} {'Date':<20} {'Type':<12} {'Amount':>12} {'Balance':>12} {'Status':<10}")
            print("-" * 80)
            for txn in reversed(transactions):
                print(f"  {txn.transaction_id:<20} {txn.timestamp:<20} {txn.transaction_type:<12} "
                      f"₹{txn.amount:>10,.2f} ₹{txn.balance_after:>10,.2f} {txn.status:<10}")
            print("-" * 80)

        input("\n  Press Enter to continue...")

def create_sample_accounts(atm: ATM):
    sample_accounts = [
        ("1234567890", "1234", 15000.00, "John Doe"),
        ("0987654321", "5678", 25000.00, "Jane Smith"),
        ("1122334455", "9012", 5000.00, "Bob Johnson"),
        ("5544332211", "3456", 75000.00, "Alice Brown"),
    ]

    print("\n" + "=" * 50)
    print("  Loading sample accounts...".center(50))
    print("=" * 50)

    for acc_num, pin, balance, holder in sample_accounts:
        atm.add_account(acc_num, pin, balance, holder)
        print(f"  ✅ Added account: {acc_num} - {holder}")
        print(f"     PIN: {pin} (demo only)")

    print(f"\n  📊 Total accounts loaded: {len(sample_accounts)}")

def main():
    try:
        atm = ATM("ATM001", "Main Branch")
        interface = ATMInterface(atm)

        create_sample_accounts(atm)

        while True:
            interface.show_welcome_screen()

            account_number = interface.get_user_input("\n  Enter account number: ", "string")
            if account_number is None or account_number.lower() == 'q':
                print("\n  Thank you for using our ATM. Goodbye!")
                break

            print("\n" + "-" * 50)
            pin = interface.get_pin_input("  Enter PIN: ")

            if not pin:
                print("\n  ❌ PIN is required.")
                input("  Press Enter to continue...")
                continue

            success, message = atm.authenticate(account_number, pin)

            if success:
                print(f"\n  ✅ {message}")
                interface.show_loading_animation()
                interface.run_transaction()
            else:
                print(f"\n  ❌ {message}")
                account = atm.accounts.get(account_number)
                if account and account.is_locked:
                    interface.show_account_locked_message()
                input("\n  Press Enter to continue...")

            if account_number in atm.accounts and atm.accounts[account_number].is_locked:
                if not interface.get_user_input("\n  Account is locked. Would you like to try another account? (Y/N): ", "yes_no") in ['y', 'yes']:
                    print("\n  Thank you for using our ATM. Goodbye!")
                    break

    except KeyboardInterrupt:
        print("\n\n  👋 Thank you for using the ATM System. Goodbye!")
    except Exception as e:
        print(f"\n  ❌ An unexpected error occurred: {str(e)}")
        print("  Please contact customer support.")

if __name__ == "__main__":
    main()
