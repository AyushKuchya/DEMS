import sqlite3

"""conn = sqlite3.connect("kchyaayush.db", check_same_thread=False)
db = conn.cursor()
columns = ['Email', 'Company Name', 'Company Number', 'Company Address', 'password']

def add_to_table(dictionay):
    dictionay = dict(dictionay)
    key = tuple(dictionay.keys())
    value = tuple(dictionay.values())

    with conn:
        db.execute("INSERT INTO 'Profiles' " + str(key) + " VALUES " + str(value))"""



"""info = {}

info['name'] = input('name: ')

info['number'] = input('number: ')

info['email'] = input('email: ')
"""

"""
if not len(db.execute('SELECT name from sqlite_master where type= "table"').fetchall()):
    #make tables
    print("Make table")
else:
    print('tabke')
"""


conn = sqlite3.connect('database/kuchyaayush.db')
db = conn.cursor()

print(type(db.execute('SELECT * FROM Employee').fetchall()[0][-1]))