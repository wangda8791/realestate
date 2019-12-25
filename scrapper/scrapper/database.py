import sqlite3

con = sqlite3.connect('realestate.db')
cur = con.cursor()

cur.execute("""create table realestate_tb (
                link text,
                address text,
                description text,
                image_url text,
                owner_name text,
                owner_contact text,
                active_search text
            )""")

con.commit()
con.close()
