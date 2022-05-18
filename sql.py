import mysql.connector
from mysql.connector import Error
import time

def create_server_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        #print("MySQL Database connection successful")
    except Error as err:
        print(f"Connect Error: '{err}'")

    return connection
    
def execute_query(connection, query):
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        #print("Query successful")
    except Error as err:
        print(f"Query Error: '{err}'")
        
def read_query(connection, query):
    try:
        cursor = connection.cursor()
        result = None
        cursor.execute(query)
        result = cursor.fetchall()
        connection.commit()
        return result
    except Error as err:
        print(f"Read Error: '{err}'")


if __name__ == "__main__":
    # create_data_table = """
    # CREATE TABLE kyro_temps (sensor_index INT PRIMARY KEY,sensor_name VARCHAR(40) NOT NULL,resistance FLOAT(24));
     # """
     
    # add_values = """
    # INSERT INTO kyro_temps VALUES
    # (1,  'Stage 1', '1600'),
    # (2,  'Stage 2', '3000'),
    # (3,  'Magnet A', '3200'),
    # (4,  'Magnet B', '4100'),
    # (5,  'Switch', '3300');
    # """

    # update_value = """
    # UPDATE kyro_temps
    # """

    # connection = create_server_connection("localhost", "root", "cuebit", "data")
    # execute_query(connection, add_values) # Execute our defined query
    
    
    query_format = f'''
    SELECT value FROM hv_rack_values WHERE name = "CATHODE_V_R";
    '''
    connection = create_server_connection("130.127.189.200", "cuebit", "cuebit", "data")
    
    while True:
        # connection = create_server_connection("localhost", "root", "cuebit", "data")
        print(read_query(connection, query_format)[0][0])
        time.sleep(1)

def get_value(table, value):
    query_format = f'''
    SELECT value FROM {table} WHERE name = "{value}";
    '''
    connection = create_server_connection("130.127.189.200", "cuebit", "cuebit", "data")
    return read_query(connection, query_format)[0][0]