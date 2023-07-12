import random
import sqlite3

conn = sqlite3.connect('card.s3db')
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS card(id INTEGER, number TEXT, pin TEXT, balance INTEGER DEFAULT 0);')
conn.commit()


def creation():
    while True:
        IIN = '400000'
        accnumber = str(random.randint(0, 999999999)).rjust(9, '0')
        checksum = str(luhn(IIN+accnumber))
        cardnum = IIN+accnumber+checksum
        cur.execute('SELECT * FROM card WHERE number=?;', (cardnum,))
        created = cur.fetchone()
        conn.commit()
        if not created:
            break
    PIN = str(random.randint(0, 9999)).rjust(4, '0')
    cur.execute('INSERT INTO card (number, pin) VALUES (?, ?);', (cardnum, PIN))
    conn.commit()
    print(f'\nYour card has been created\nYour card number:\n{cardnum}\nYour card PIN:\n{PIN}\n')


def login():
    CN = input('\nEnter your card number:\n')
    PIN = input('Enter your PIN:\n')
    cur.execute("SELECT pin FROM card WHERE number=? and pin=?;", (CN, PIN))
    authen = cur.fetchone()
    conn.commit()
    if authen:
        print('\nYou have successfully logged in!\n')
        accmenu(CN)
    else:
        print('\nWrong card number or PIN!\n')


def accmenu(cardnum):
    while True:
        accchoice = input('1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit\n')
        if accchoice == '0':
            print('\nBye!')
            exit()
        elif accchoice == '1':
            print(balance(cardnum))
        elif accchoice == '2':
            print(add(cardnum))
        elif accchoice == '3':
            print(transfer(cardnum))
        elif accchoice == '4':
            print(close(cardnum=cardnum))
            break
        elif accchoice == '5':
            print('\nYou have successfully logged out!\n')
            break


def balance(cardnum):
    cur.execute("SELECT balance FROM card WHERE number=?;", (cardnum,))
    bal = cur.fetchone()[0]
    conn.commit()
    return f'\nBalance: {bal}\n'


def luhn(carddigits):
    luhnfunc = sum([eval(x)*2-9 if eval(x)*2 > 9 else eval(x)*2 for x in carddigits[::2]]) + \
           sum([eval(x) for x in carddigits[1::2]])
    checksum = (10-luhnfunc % 10) % 10
    return str(checksum)


def add(cardnum):
    income = input('\nEnter income:\n')
    cur.execute('UPDATE card SET balance=balance+? WHERE number=?;', (int(income), cardnum))
    conn.commit()
    return "Income was added!\n"


def transfer(cardnum):
    targetcard = input('\nTransfer\nEnter card number:\n')
    if luhn(targetcard[:-1]) != targetcard[-1]:
        return 'Probably you made a mistake in the card number. Please try again!\n'
    cur.execute("SELECT balance FROM card WHERE number=?;", (targetcard,))
    tar = cur.fetchone()
    conn.commit()
    if tar is None:
        return 'Such a card does not exist.\n'
    amount = int(input('Enter how much money you want to transfer:'))
    cur.execute("SELECT balance FROM card WHERE number=?;", (cardnum,))
    bal = cur.fetchone()
    conn.commit()
    if int(bal[0]) < amount:
        return 'Not enough money!\n'
    else:
        cur.execute('UPDATE card SET balance=balance+? WHERE number=?;', (int(amount), targetcard))
        conn.commit()
        cur.execute('UPDATE card SET balance=balance-? WHERE number=?;', (int(amount), cardnum))
        conn.commit()
        return 'Success!\n'


def close(cardnum):
    cur.execute('DELETE FROM card WHERE number=?;', (cardnum,))
    conn.commit()
    return '\nThe account has been closed!\n'


def menu():
    while True:
        choice = input('1. Create an account\n2. Log into account\n0. Exit\n')
        if choice == '0':
            print('\nBye!')
            break
        elif choice == '1':
            creation()
        elif choice == '2':
            login()


if __name__ == "__main__":
    menu()
