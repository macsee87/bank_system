import sqlite3
import random
import os.path

# check if the database already exists
if not os.path.isfile('card.s3db'):
    conn = sqlite3.connect('card.s3db')     # Make the connection with the database
    c = conn.cursor()                       # Create a cursor
    # Create table
    c.execute('''CREATE TABLE card(id INTEGER,number TEXT,pin TEXT,balance INTEGER DEFAULT 0);''')
else:
    # Make connection with the database and create a cursor
    conn = sqlite3.connect('card.s3db')
    c = conn.cursor()


class Bank:
    STATUS_OFF = -1
    STATUS_IDLE = 0
    STATUS_WAIT_CARD_NUMBER = 1
    STATUS_WAIT_PIN = 2
    STATUS_USER_LOGGED = 3
    _MENU_MAIN = "    <<  MENU >>\n1. Create an account\n2. Log into account\n0. Exit\n"
    _MENU_USER = "\n1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit"
    _MSG_LOGIN_SUCCESS = "\nYou have successfully logged in!"
    _MSG_LOGIN_FAIL = "\nWrong card number or PIN!"
    _MSG_SUCCESS = "\nSuccess!"
    _MSG_NOT_ENOUGH_MONEY = "Not enough money!"
    _MSG_ANOTHER_ACCOUNT = "\nYou can't transfer money to the same account!"
    _MSG_CHECKSUM_FAIL = "\nProbably you made mistake in the card number. Please try again!"
    _MSG_INCOME_AMOUNT = "\nEnter income:\n"
    _MSG_INCOME_ADDED = "Income was added!\n"
    _MSG_CLOSE_ACCOUNT = "\nThe account has been closed!"
    _MSG_BYE = "\nBye!"

    def __init__(self):
        self.status = Bank.STATUS_IDLE
        self.prompt = Bank._MENU_MAIN
        self.login_card = ""

    def main_menu(self):
        if self.status == Bank.STATUS_IDLE:
            main_choice = input()
            if main_choice == '0':
                exit()
            if main_choice == '1':
                self.create_account()
            elif main_choice == '2':
                self.log_in()

        elif self.status == Bank.STATUS_USER_LOGGED:
            logged_choice = input()
            if logged_choice == '0':
                print(Bank._MSG_BYE)
                exit()
            if logged_choice == '1':
                self.status = Bank.STATUS_USER_LOGGED
                print(f"Balance: {self.select_balance(self.login_card)}\n")

            if logged_choice == '2':
                self.status = Bank.STATUS_USER_LOGGED
                n_income = int(input(Bank._MSG_INCOME_AMOUNT))
                self.add_income(n_income, self.login_card)

            if logged_choice == '3':
                self.status = Bank.STATUS_USER_LOGGED
                to_account = input("Transfer\nEnter card number:\n")
                if self.checksum(number=to_account[0:15]) == to_account[15]:
                    if self.check_account(to_account) == to_account:
                        if self.login_card != to_account:
                            n_transfer = int(input("\nEnter how much money you want to transfer:\n"))
                            if self.select_balance(card_number=self.login_card) >= n_transfer:
                                self.do_transfer(to_account, n_transfer, card_number=self.login_card)
                                return
                            else:
                                return print(Bank._MSG_NOT_ENOUGH_MONEY)
                        else:
                            return print(Bank._MSG_ANOTHER_ACCOUNT)
                    else:
                        return print(Bank._MSG_CHECKSUM_FAIL)
                else:
                    return print(Bank._MSG_CHECKSUM_FAIL)

            if logged_choice == '4':
                self.status = Bank.STATUS_USER_LOGGED
                self.close_account(card_number=self.login_card)
                self.status = Bank.STATUS_IDLE
                self.prompt = Bank._MENU_MAIN
                return

            if logged_choice == '5':
                self.status = Bank.STATUS_IDLE
                self.prompt = Bank._MENU_MAIN
                return '\nYou have successfully logged out!\n'

    def create_account(self):
        new_card_number = self.card_number_generator()
        new_pin = f"{random.randint(0, 9999):04}"
        self.save_new_account(new_card_number, new_pin)
        print("\nYour card has been created\nYour card number:\n" f"{new_card_number}"
                "\nYour card PIN:\n" f"{new_pin}")

    def log_in(self):
        self.login_card = input('\nEnter your card number:\n')
        login_pin = input('Enter your PIN:\n')
        c.execute(f'SELECT * FROM card WHERE number = ? AND pin = ?', (self.login_card, login_pin))
        if c.fetchone() is None:
            print(Bank._MSG_LOGIN_FAIL)
        else:
            self.status = Bank.STATUS_USER_LOGGED
            self.prompt = Bank._MENU_USER
            self.login_card = self.login_card
            print(Bank._MSG_LOGIN_SUCCESS)

    def card_number_generator(self):
        iin = '400000'
        can = ''
        for i in range(9):
            n = str(random.randint(0, 9))
            can += n
        checksum = self.checksum(iin + can)
        return iin + can + checksum

    def checksum(self, number):
        number_list = [int(num) for num in number]
        for index in range(0, 15, 2):
            number_list[index] *= 2
            if number_list[index] > 9:
                number_list[index] -= 9
        checker = 0
        while (checker + sum(number_list)) % 10 != 0:
            checker += 1
        return str(checker)

    def save_new_account(self, card_number, pin):
        c.execute(f'INSERT INTO card(number, pin) VALUES (?,?)', (card_number, pin))
        conn.commit()

    def select_balance(self, card_number):
        c.execute(f'select balance from card where number = %s' % card_number)
        return int(c.fetchone()[0])

    def add_income(self, n_income, card_number):
        c.execute(f'update card set balance = (balance + %d) where number = %s' % (n_income, card_number))
        conn.commit()
        return print(Bank._MSG_INCOME_ADDED)

    def do_transfer(self, to_account: str, n_transfer: int, card_number):
        c.execute('update card set balance = (balance - %d) where number = %s' % (n_transfer, card_number))
        conn.commit()
        c.execute('update card set balance = (balance + %d) where number = %s' % (n_transfer, to_account))
        conn.commit()
        return print(Bank._MSG_SUCCESS)

    def check_account(self, to_account: str) -> bool:
        c.execute('select number from card where number = %s' % to_account)
        try:
            return c.fetchone()[0]
        except:
            print('Not exists card!')
            return

    def close_account(self, card_number):
        c.execute('delete from card where number = %s' % card_number)
        conn.commit()
        return Bank._MSG_CLOSE_ACCOUNT

my_bank = Bank()
while my_bank.status != Bank.STATUS_OFF:
    print(my_bank.prompt)
    print(my_bank.main_menu())

conn.close()
