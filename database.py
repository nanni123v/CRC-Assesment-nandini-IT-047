import sqlite3


connection=sqlite3.connect("sql.db")

cur = connection.cursor()
cur.execute("""
create table if not exists shipment(
    id INTEGER,
    weight REAL,
    content TEXT,
    status TEXT)
            


""")



# insert data



cur.execute("""
            
insert into shipment values(1270,12.5,"cpu","placed")            
            
            
            """)
# fetch data


cur.execute("""
            
 select * from shipment where id =1270           
            """)

data = cur.fetchall()

print(data)
#UPDATE 
content = "xyz" 
id = 1270
cur.execute("""
 UPDATE shipment 
 SET content =? 
 WHERE id =?       
            """, (content, id))




connection.commit()

connection.close()