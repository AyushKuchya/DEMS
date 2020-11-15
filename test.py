import sqlite3
company_profile_ = sqlite3.connect("database/final.db")
                                                  
companies_db = company_profile_.cursor()
with company_profile_:
    print(companies_db.execute("SELECT * FROM WorksOn").fetchall())
