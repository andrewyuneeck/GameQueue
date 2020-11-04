import mysql.connector

db_conn = mysql.connector.connect(user="root",
                            password="andrew13",
                            host="acit3855-lab6-docker.westus2.cloudapp.azure.com",
                            port="3306",
                            database="events")
db_cursor = db_conn.cursor()

db_cursor.execute('''
                  DROP TABLE zone1, zone2
                  ''')

db_conn.commit()
db_conn.close()

