import mysql.connector

db_conn = mysql.connector.connect(user="root",
                            password="andrew13",
                            host="acit3855-lab6-docker.westus2.cloudapp.azure.com",
                            port="3306",
                            database="events")
db_cursor = db_conn.cursor()

db_cursor.execute('''
    CREATE TABLE zone1
          (id INT NOT NULL AUTO_INCREMENT, 
           player_id VARCHAR(250) NOT NULL,
           ranking VARCHAR(100) NOT NULL,
           num_player_total INT NOT NULL,
           timestamp VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           CONSTRAINT zone1_pk PRIMARY KEY (id))
          ''')

db_cursor.execute('''
    CREATE TABLE zone2
          (id INT NOT NULL AUTO_INCREMENT, 
           player_id VARCHAR(250) NOT NULL,
           ranking VARCHAR(100) NOT NULL,
           num_player_total INT NOT NULL,
           timestamp VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           CONSTRAINT zone2_pk PRIMARY KEY (id))
          ''')

db_conn.commit()
db_conn.close()
