import sqlite3


def start_connection(database:str):
    connection = sqlite3.connect(database,check_same_thread=False)
    return connection


def create_table(table , connection, **columns) :
    cursor = connection.cursor()
    columns_str = ", ".join(f"{name} {data_type}" for name, data_type in columns.items())
    cursor.execute(f"""CREATE TABLE IF NOT EXISTS {table} ({columns_str})""")
    connection.commit()


# check if record already exists before adding it to database , if so , don't add it
def record_already_exists(table , connection , fields:tuple ):
    records = fetch_all_db_records(table , connection)
    for record in records : 
        if record[1] == fields[0] and float(record[2])==float(fields[1]) and int(record[3])==int(fields[2]):
            return True
    return False

def insert_db_record(table , connection , fields : tuple) : 
    cursor = connection.cursor()
    if record_already_exists(table, connection , fields) : return False
    place_holders = ",".join("?" for _ in range(len(fields)))
    cursor.execute(f"INSERT INTO {table} VALUES({place_holders})  " , fields) # cursor.execute(f"INSERT INTO {table} VALUES({'?'*len(fields)}) " , fields) why doesnt it work ? 
    connection.commit()
    return True

def insert_many_db_records(table , connection , records:list) : 
    cursor = connection.cursor()
    
    # eligible_records are records that do not already exist in database table
    eligible_records = []
    for record in records : 
        if record_already_exists(table , connection , record): continue
        eligible_records.append(record[1:])
    
    if not eligible_records : return
    
    place_holders = ",".join("?" for _ in range(len(eligible_records[0])))
    cursor.executemany(f"INSERT INTO {table} VALUES({place_holders})",eligible_records)
    connection.commit()

def insert_many_db_records_supported_currencies(table , connection , records:list) : 
    cursor = connection.cursor()
        
    cursor.executemany(f"INSERT INTO {table}(symbol) VALUES(?)",records)
    connection.commit()

def fetch_db_record(table , id ,connection):
    cursor = connection.cursor()
    cursor.execute(f"SELECT * from {table} WHERE rowid={id}")
    return cursor.fetchall()

def fetch_all_db_records(table ,connection) :
    cursor = connection.cursor()
    cursor.execute(f"SELECT rowid,* from {table}")
    return cursor.fetchall()

def delete_record(table , id , connection) :
    cursor = connection.cursor()
    cursor.execute(f"DELETE FROM {table} WHERE rowid = {id}")
    connection.commit()
    
    #when we delete a record , the ids won't rearrange automatically, we must do it manually by 
    # backing up the data , then deleting all records , then inserting all data so that ids are consecutive
    records = fetch_all_db_records(table , connection)
    if not records : return
    cursor.execute(f"DELETE FROM {table}")
    insert_many_db_records(table , connection ,records)
    connection.commit()
    


def delete_all_records(table , connection) : 
    cursor = connection.cursor()
    cursor.execute(f"DELETE FROM {table}")
    connection.commit()


def delete_table(table ,connection) :
    cursor = connection.cursor()
    cursor.execute(f"DROP TABLE {table} ")
    connection.commit()

def close_connection(connection ) : 
    cursor = connection.cursor()
    cursor.close()
    connection.close()
    

if __name__=="__main__" : 
    connection = start_connection("Temp")
    create_table("Crypto" , connection , symbol="TEXT" , price = "REAL" , amount_owned = "INTEGER")
    records = [("BTC" , 25000 , 2) , ("BNB" , 219 , 100) , ("XMR",130 , 4) ]
    insert_db_record("Crypto" , connection , records[0])

    




#make create_table accepts dict instead of **columns
# if record already exist , make a pop-up message to tell the user
