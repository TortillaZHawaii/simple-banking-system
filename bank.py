import random
import sqlite3


# Starts connection to database using sqlite3
conn = sqlite3.connect('card.s3db')


# Creates table card:
# id, number, pin, balance
def create_database():
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS card ('
                '   id INTEGER PRIMARY KEY AUTOINCREMENT,'
                '   number TEXT,'
                '   pin TEXT,'
                '   balance INTEGER DEFAULT 0'
                ');')
    conn.commit()


# Displays card table in command line
def view_database():
    cur = conn.cursor()
    cur.execute('SELECT * FROM card;')
    print("(id, number, pin, balance)")
    for row in cur:
        print(row)


# Drops main table
def clear_database():
    cur = conn.cursor()
    cur.execute('DROP TABLE card;')
    conn.commit()


# Main menu
def menu():
    options = {1: "Create an account",
               2: "Log into account",
               # 3: "View database", # Uncomment this to view database on fly
               0: "Exit"}

    flag = True
    while flag:
        for i, text in options.items():
            print(str(i) + ". " + text)

        pressed_key = int(input())
        print()
        if pressed_key in options.keys():
            if pressed_key == 0:
                break

            elif pressed_key == 1:
                create_account()

            elif pressed_key == 2:
                flag = log_in_menu()

            elif pressed_key == 3:
                view_database()

    print("Bye!")


# Log in menu
def log_in_menu():
    # Retrieve details
    card_number = input("Enter your card number: ")
    pin = input("Enter your PIN: ")

    # Find in database
    cur = conn.cursor()
    cur.execute('SELECT number, balance FROM card WHERE number = ? AND pin = ?;',
                (card_number, pin))

    account = cur.fetchone()  # account = (card_number, balance) OR None if pin doesn't match up

    # Successful log in
    if account:
        print("You have successfully logged in!")
        options = {1: "Balance",
                   2: "Add income",
                   3: "Do transfer",
                   4: "Close account",
                   5: "Log out",
                   0: "Exit"}

        while True:
            # Basic menu action
            for i, text in options.items():
                print(str(i) + ". " + text)

            pressed_key = int(input())
            print()

            if pressed_key in options.keys():
                if pressed_key == 0:  # Exit
                    return False

                elif pressed_key == 1:  # Balance
                    print("Balance:", balance(card_number, pin))

                elif pressed_key == 2:  # Income
                    income = int(input("Enter income:\n"))

                    # Update database
                    cur.execute('UPDATE card SET balance = balance + ? WHERE number = ? AND pin = ?;',
                                (income, card_number, pin))
                    conn.commit()

                    print("Income was added!")

                elif pressed_key == 3:  # Transfer
                    print("Transfer")
                    transfer_to_card = input("Enter a card number:\n")

                    if is_card_number_valid(transfer_to_card):
                        # Try to find this card number
                        cur.execute('SELECT * FROM card WHERE number = ?;',
                                    (transfer_to_card,))
                        row = cur.fetchone()

                        if row:
                            transfer_amount = int(input("Enter how much money you want to transfer:\n"))
                            if transfer_amount <= balance(card_number, pin):
                                # Do transfer
                                cur.execute('UPDATE card SET balance = balance + ? WHERE number = ?;',
                                            (transfer_amount, transfer_to_card))
                                conn.commit()
                                cur.execute('UPDATE card SET balance = balance - ? WHERE number = ?;',
                                            (transfer_amount, card_number))
                                conn.commit()
                                print("Success!\n")
                            else:
                                print("Not enough money!\n")
                        else:
                            print("Such a card does not exist.\n")

                    else:
                        print("Probably you made a mistake in the card number. Please try again!\n")

                elif pressed_key == 4:  # Delete
                    cur.execute('DELETE FROM card WHERE number = ?',
                                (card_number,))
                    conn.commit()
                    print("The account has been closed!\n")
                    break

                elif pressed_key == 5:  # Log out
                    print("You have successfully logged out!\n")
                    break

            else:
                print("Wrong key\n")

    # Wrong pin or card number
    else:
        print("Wrong card number or PIN!\n")

    return True


# Gets balance from account
def balance(card_number, pin):
    cur = conn.cursor()
    cur.execute('SELECT balance FROM card WHERE number = ? AND pin = ?',
                (card_number, pin))
    return cur.fetchone()[0]  # row = (balance, )


# Creates an account
def create_account():
    pin = generate_pin()
    card_number = generate_card_number()

    cur = conn.cursor()
    cur.execute('INSERT INTO card (number, pin) VALUES (?,?)', (card_number, pin))
    conn.commit()

    print("Your card has been created")
    print("Your card number:")
    print(card_number)
    print("Your card PIN:")
    print(pin)


# Generates random 4 digit pin
def generate_pin():
    return generate_random_str(4)


# Creates a random string of digits of length n
def generate_random_str(n):
    return ''.join([str(random.randint(1, 9)) for _ in range(n)])


# Generates card number that starts with start="400000" (BIN) and uses Luhn algorithm for last digit
def generate_card_number(start="400000"):
    without_luhn = start + generate_random_str(9)
    after_luhn = [int(x) for x in without_luhn]
    for i in range(len(after_luhn)):
        if i % 2 == 0:
            after_luhn[i] *= 2
            if after_luhn[i] > 9:
                after_luhn[i] -= 9

    sum_after = sum(after_luhn)
    luhn = 0
    if sum_after % 10 != 0:
        luhn = sum_after // 10 * 10 + 10 - sum_after

    return without_luhn + str(luhn)


# Checks if card number is valid based on Luhn algorithm
def is_card_number_valid(card_number):
    if len(card_number) != 16:
        return False

    after_luhn = [int(x) for x in card_number]
    for i in range(len(after_luhn)):
        if i % 2 == 0:
            after_luhn[i] *= 2
            if after_luhn[i] > 9:
                after_luhn[i] -= 9

    return sum(after_luhn) % 10 == 0


# clear_database() # Uncomment this to clear the database
create_database()
menu()
