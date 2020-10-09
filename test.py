import sqlite3

conn = sqlite3.connect("companies.db", check_same_thread=False)
db = conn.cursor()
columns = ['Email', 'Company Name', 'Company Number', 'Company Address', 'password']

def add_to_table(dictionay):
    dictionay = dict(dictionay)
    key = tuple(dictionay.keys())
    value = tuple(dictionay.values())

    with conn:
        db.execute("INSERT INTO 'Profiles' " + str(key) + " VALUES " + str(value))



"""info = {}

info['name'] = input('name: ')

info['number'] = input('number: ')

info['email'] = input('email: ')
"""

with conn:
    print(db.execute("SELECT * FROM 'Profiles'").fetchall())
