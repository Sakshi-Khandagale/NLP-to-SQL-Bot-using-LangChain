import sqlite3

# connect to sqllite 
connection = sqlite3.connect("student.db")

#create a cursor object to insert record, create table 
# cursor (Object to run and fetch SQL queries)

cursor = connection.cursor()

# create the table 
table_info ='''
create table STUDENT (NAME VARCHAR(25), CLASS VARCHAR(25),
SECTION VARCHAR (25),MARKS INT)
'''
cursor.execute(table_info)        # excuting 

# insert some more records
cursor.execute('''Insert Into STUDENT values (' Muskan', 'Data Scientist', 'A', 98) ''')
cursor.execute('''Insert Into STUDENT values (' Neelam', 'Data Scientist', 'B', 100) ''')
cursor.execute('''Insert Into STUDENT values (' Vishant', 'Data Scientist', 'A', 86) ''')
cursor.execute('''Insert Into STUDENT values (' Nawed ', 'DEVOPS', 'A', 80) ''')
cursor.execute('''Insert Into STUDENT values (' Manal', 'DEVOPS', 'A', 78) ''')

# Display all the records 
print ("The inerted records are")
data=cursor.execute('''Select * from STUDENT''')
for row in data:
    print(row)


# commit your changes in the database 
connection.commit()
connection.close()




