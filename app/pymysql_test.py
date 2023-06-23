# Required packages and libraries
# pip install pymysql
# pip install cryptography

import sys
# table = str(sys.argv[1])
# print(table)
# How to connect to a MySQL database using pymysql
# Steps for Python's DB-API (source: Head First Python)

# Step 1: Define your connection characteristics
# Need four pieces of information to connect to MySQL: 1. IP address/host,
# 2. user id, 3. password (corresponding to the user id), 4. database name
dbconfig = {'host': '127.0.0.1',
            'user': 'testuser',
            'password': 'testpasswd',
            'database': 'testDB',
            }

# Step 2: Import your Database driver
import pymysql

# Step 3: Establish a connection to the server
conn = pymysql.connect(**dbconfig,
                       cursorclass=pymysql.cursors.DictCursor)
    # You can leave out cursorclass to get the results as a list of tuples.

with conn:
    with conn.cursor() as cursor:
        try:
            _SQL = "SELECT * FROM user_login WHERE username=%s"
            cursor.execute(_SQL, ('sindhu',))
            result = cursor.fetchall()
            print(result)
        except Exception as err:
            raise Exception(err)