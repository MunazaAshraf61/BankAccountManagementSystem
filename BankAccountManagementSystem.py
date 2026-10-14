import csv
import os
from abc import ABC, abstractmethod
from datetime import datetime


class BankAccount(ABC):
    def __init__(self, account_number, name, balance=0.0):
        self.account_number = account_number
        self.name = name
        self.balance = balance

    @abstractmethod
    def display_details(self):
        pass

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit amount must be greater than zero.")

        self.balance += amount
        return self.balance

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Withdrawal amount must be greater than zero.")

        if amount > self.balance:
            raise ValueError("Insufficient balance.")

        self.balance -= amount
        return self.balance



class SavingsAccount(BankAccount):
    def display_details(self):
        print("\n----- Account Details -----")
        print(f"Account Number: {self.account_number}")
        print(f"Account Holder: {self.name}")
        print(f"Account Type: Savings Account")
        print(f"Current Balance: Rs. {self.balance:.2f}")


class Bank:
    ACCOUNT_FILE = "accounts.csv"
    TRANSACTION_FILE = "transactions.csv"

    def __init__(self):
        self.accounts = {}
        self.load_accounts()
        self.create_transaction_file()

    def load_accounts(self):
        #load saved accounts when the program starts
        if not os.path.exists(self.ACCOUNT_FILE):
            return

        try:
            with open(self.ACCOUNT_FILE, "r", newline="") as file:
                reader = csv.DictReader(file)

                for row in reader:
                    account = SavingsAccount(
                        row["account_number"],
                        row["name"],
                        float(row["balance"])
                    )
                    self.accounts[account.account_number] = account

        except (OSError, ValueError, KeyError, csv.Error) as error:
            print(f"Error loading accounts: {error}")

    def save_accounts(self):
        #save all account details to a CSV file
        with open(self.ACCOUNT_FILE, "w", newline="") as file:
            fieldnames = ["account_number", "name", "balance"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            writer.writeheader()

            for account in self.accounts.values():
                writer.writerow({
                    "account_number": account.account_number,
                    "name": account.name,
                    "balance": f"{account.balance:.2f}"
                })

    def create_transaction_file(self):
        #create transaction history file if it does not exist
        if not os.path.exists(self.TRANSACTION_FILE):
            with open(self.TRANSACTION_FILE, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([
                    "Date and Time",
                    "Account Number",
                    "Transaction Type",
                    "Amount",
                    "Balance After Transaction"
                ])

    def record_transaction(self, account, transaction_type, amount):
        #append a transaction without deleting older records
        with open(self.TRANSACTION_FILE, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                account.account_number,
                transaction_type,
                f"{amount:.2f}",
                f"{account.balance:.2f}"
            ])

    def create_account(self):
        account_number = input("Enter a new account number: ").strip()

        if not account_number:
            print("Account number cannot be empty.")
            return

        if account_number in self.accounts:
            print("This account number already exists.")
            return

        name = input("Enter account holder name: ").strip()

        if not name:
            print("Account holder name cannot be empty.")
            return

        try:
            initial_balance = float(
                input("Enter initial deposit (Rs.): ")
            )

            if initial_balance < 0:
                print("Initial deposit cannot be negative.")
                return

            account = SavingsAccount(
                account_number, name, initial_balance
            )

            self.accounts[account_number] = account
            self.save_accounts()

            if initial_balance > 0:
                self.record_transaction(
                    account, "Initial Deposit", initial_balance
                )

            print("Account created successfully!")

        except ValueError:
            print("Please enter a valid amount.")

        except OSError as error:
            self.accounts.pop(account_number, None)
            print(f"File error while creating account: {error}")

    def find_account(self):
        account_number = input("Enter account number: ").strip()

        if account_number not in self.accounts:
            print("Account not found.")
            return None

        return self.accounts[account_number]

    def deposit_money(self):
        account = self.find_account()

        if account is None:
            return

        try:
            amount = float(input("Enter deposit amount (Rs.): "))
            account.deposit(amount)

            self.save_accounts()
            self.record_transaction(account, "Deposit", amount)

            print(f"Rs. {amount:.2f} deposited successfully.")
            print(f"Available balance: Rs. {account.balance:.2f}")

        except ValueError as error:
            print(f"Invalid deposit: {error}")

        except OSError as error:
            print(f"File error: {error}")

    def withdraw_money(self):
        account = self.find_account()

        if account is None:
            return

        try:
            amount = float(input("Enter withdrawal amount (Rs.): "))
            account.withdraw(amount)

            self.save_accounts()
            self.record_transaction(account, "Withdrawal", amount)

            print(f"Rs. {amount:.2f} withdrawn successfully.")
            print(f"Available balance: Rs. {account.balance:.2f}")

        except ValueError as error:
            print(f"Invalid withdrawal: {error}")

        except OSError as error:
            print(f"File error: {error}")

    def check_balance(self):
        account = self.find_account()

        if account is not None:
            print(
                f"Available balance: Rs. {account.balance:.2f}"
            )

    def show_account_details(self):
        account = self.find_account()

        if account is not None:
            account.display_details()

    def show_transaction_history(self):
        account = self.find_account()

        if account is None:
            return

        try:
            with open(self.TRANSACTION_FILE, "r", newline="") as file:
                reader = csv.DictReader(file)
                found = False

                print("\n----- Transaction History -----")

                for row in reader:
                    if row["Account Number"] == account.account_number:
                        found = True
                        print(
                            f"Date: {row['Date and Time']} | "
                            f"Type: {row['Transaction Type']} | "
                            f"Amount: Rs. {row['Amount']} | "
                            f"Balance: Rs. "
                            f"{row['Balance After Transaction']}"
                        )

                if not found:
                    print("No transactions found for this account.")

        except (OSError, csv.Error, KeyError) as error:
            print(f"Error reading transaction history: {error}")

    def run(self):
        while True:
            print("\n===== BANK ACCOUNT MANAGEMENT SYSTEM =====")
            print("1. Create Account")
            print("2. Deposit Money")
            print("3. Withdraw Money")
            print("4. Check Balance")
            print("5. Display Account Details")
            print("6. View Transaction History")
            print("7. Exit")

            choice = input("Enter your choice (1-7): ").strip()

            try:
                if choice == "1":
                    self.create_account()
                elif choice == "2":
                    self.deposit_money()
                elif choice == "3":
                    self.withdraw_money()
                elif choice == "4":
                    self.check_balance()
                elif choice == "5":
                    self.show_account_details()
                elif choice == "6":
                    self.show_transaction_history()
                elif choice == "7":
                    print("Thank you for using our banking system!")
                    break
                else:
                    print("Invalid choice. Please select from 1 to 7.")

            except OSError as error:
                print(f"File operation failed: {error}")



if __name__ == "__main__":
    bank = Bank()
    bank.run()
