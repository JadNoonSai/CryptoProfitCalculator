from tkinter import * 
from tkinter import messagebox
from tkmacosx import Button as macButton
import json,requests,threading,database,time



#To avoid using global row_index variable
class Row_Index_Manager() : 
    row_index = 0 
    
    @staticmethod
    def get_row_index():return Row_Index_Manager.row_index
    
    @staticmethod
    def set_row_index(new_row_index): Row_Index_Manager.row_index=new_row_index
    
    @staticmethod
    def increase_row_index():Row_Index_Manager.row_index+=1
    

# to avoid using global api variable
class Api_Manager : 
    api = None
    flag = False
    
    @staticmethod
    def get_api():return Api_Manager.api
    
    @staticmethod
    def set_api(api): 
        Api_Manager.api = api
        Api_Manager.flag = True
    
    def reset_flag() : Api_Manager.flag = False


def create_window():
    pycrypto = Tk()
    pycrypto.title("My Crypto Portfolio")
    # pycrypto.resizable(False,False)
    return pycrypto


def get_headers() :
    columns = ["id",
            "Coin Name" , 
            "Price (At time of purchase)" ,
            "Coin Owned" , 
            "Total Amount Paid" ,
            "Price (At this moment)",
            "Current Value", 
            "P/L Per Coin" ,
            "Total P/L With Coin"
    ]
    return columns


# def get_headers_for_db() :
#     columns = {"id":"INTEGER",
#             "Coin Name" :"TEXT", 
#             "Price (At time of purchase)" : "REAL" ,
#             "Coin Owned" : "INTEGER" , 
#             "Total Amount Paid" : "REAL",
#             "Price (At this moment)":"REAL",
#             "Current Value":"REAL", 
#             "P/L Per Coin" : "REAL",
#             "Total P/L With Coin" : "REAL"
#     }
#     return columns

def create_headers(pycrypto): 
    
    columns = get_headers()

    for i in range(len(columns)): 
        name = Label(pycrypto , text = columns[i], bg = "#142E54" , fg = "white" , font = "Lato 12 bold",padx=5,pady=5,borderwidth=2,relief="groove")
        name.grid(row =Row_Index_Manager.row_index , column = i , sticky = N+S+E+W )
    Row_Index_Manager.increase_row_index()
    return len(columns)
        

def generate_example(pycrypto) : 
    example_info = [ "#" ,"XMR" , "$142.44" , "10" , "$400.50" , "$120.44","$1424.38", "$102.39" ,"$1023.88"]
    for i in range(len(example_info)) : 
        example_label = Label(pycrypto , text = example_info[i] , fg="gray" , font = "Lato 12 italic",relief="groove" , bd=2 ,bg = "white" )
        example_label.grid(row=Row_Index_Manager.row_index,column = i,sticky = N+S+E+W)
    Row_Index_Manager.increase_row_index()


def create_button(pycrypto,nb_of_headers,connection): 
    button = macButton(pycrypto, text = "Create",bg="gray",command= lambda : create_record(pycrypto,button,nb_of_headers,connection))
    button.grid(row=Row_Index_Manager.row_index,column=0,columnspan = nb_of_headers, sticky=N+S+W+E)
    
    
def create_record(pycrypto , button , nb_of_headers,connection) : 

    button.destroy()

    entries = []
    for i in range(3) : 
        entry = Entry(pycrypto , relief="groove" ,bd=2,bg="white",fg="black")
        entry.grid(row=Row_Index_Manager.row_index , column = i+1 ,sticky=N+S+W+E)
        entries.append(entry)
        
    entries[0].bind("<KeyRelease>" , lambda event , symbol_entry=entries[0]: request_api(symbol_entry.get().upper()))
        
    
    calculate_button = macButton(pycrypto,text = "Calculate",bg="#ff3300", command =lambda :  my_portfolio(pycrypto,entries,calculate_button,nb_of_headers,connection))
    calculate_button.grid(row=Row_Index_Manager.row_index,column = 4 , columnspan = nb_of_headers-3,sticky = N+S+E+W)
    


def request_api(symbol) : 
    
    url = f'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest?CMC_PRO_API_KEY=f63ff251-a883-4b92-8a3d-2685615e31bf'
    params = {'symbol': symbol}
    
    def make_request():

        try : api_request = requests.get(url, params=params) 
        except : messagebox.askretrycancel("Network Connection Problem","No Intenet Connection")
        else:
            api_got:dict = json.loads(api_request.content)
            # print(api_got)
            Api_Manager.set_api(api_got)
        
    
    # Start a new thread to make the API request
    threading.Thread(target = make_request).start()
    

def perform_operations(entries_values,currency_info) : 
    
    id  = str(Row_Index_Manager.get_row_index()-1)
    price_at_time_of_purchase ,amount_owned= float(entries_values[1]) , int(entries_values[2])
    total_paid = f'{price_at_time_of_purchase * amount_owned:.2f}'
    price_at_this_moment = f'{currency_info["quote"]["USD"]["price"]:.2f}'
    current_value = f'{amount_owned * currency_info["quote"]["USD"]["price"]:.2f}'
    pl_percoin = f'{currency_info["quote"]["USD"]["price"] - price_at_time_of_purchase:.2f}'
    total_pl_coin = f'{float(pl_percoin) * amount_owned:.2f}'
    
    return [id,entries_values[0].upper(),entries_values[1],entries_values[2],total_paid, price_at_this_moment ,current_value,pl_percoin,total_pl_coin ]

def destroy_entries(entries): 
    for entry in entries: entry.destroy()
    
    
def insert_record(pycrypto,to_insert):
    for i in range(len(to_insert)) :
        if get_headers()[i]=="P/L Per Coin" or get_headers()[i]=="Total P/L With Coin":
            font_color = get_font_color(float(to_insert[i]))
        else : font_color = "black"
        label = Label(pycrypto , text = str(to_insert[i]).upper() , relief =GROOVE , bd=2 ,fg = font_color,bg="white")
        label.grid(row=Row_Index_Manager.row_index , column = i , sticky = N+S+E+W)
        

def get_font_color(value):
    if value<0 : return "red"
    elif value==0:return "orange"
    else : return "green"

def check_entries(entries):
    flag = True
    for i in range(len(entries)) : 
        entry = entries[i]
        entry_value = entry.get()
        if not entry_value : 
            write_error(entry,"No Value Given")
            flag = False
        elif entry_value=="No Value Given" or entry_value=="Integers Only" or entry_value=="No Such Currency":
            flag=False
            continue
        elif i>0  and not entry_value.isnumeric() :
            write_error(entry , "Integers Only")
            flag = False

    if not flag : return []
    return entries
    

def write_error(entry,error_text):
    entry.delete(0,END)
    entry.config(fg="red")
    entry.insert(0,error_text)
    entry.bind("<FocusOut>" , lambda event , elm = entry: elm.config(fg="black"))

    

def my_portfolio(pycrypto,entries,calculate_button,nb_of_headers,connection) : 
    
    symbol = entries[0].get().upper()
    api = Api_Manager.get_api()
    
    if not api :  
        messagebox.askretrycancel("Network Connection Problem","Slow Intenet Connection")
        api = Api_Manager.get_api()
    
    try : currency_info = (api["data"][symbol])[0]
    except Exception as e : 
        write_error(entries[0] , "No Such Currency")
        return
     
    entries = check_entries(entries)
    if not entries:return
    entries_values = [entry.get() for entry in entries]
    
    
    to_insert = perform_operations(entries_values , currency_info)
    successful = database.insert_db_record("CryptoProfitDetector", connection , tuple(to_insert[1:])   )

    if not successful: 
        messagebox.showerror("Adding New Record" , "Record Already Exists")
        calculate_button.destroy()
        destroy_entries(entries)
        create_button(pycrypto,nb_of_headers,connection)
        return
    
    calculate_button.destroy()
    destroy_entries(entries)
    insert_record(pycrypto,to_insert) 
    
    Row_Index_Manager.increase_row_index()
    create_button(pycrypto,nb_of_headers,connection)

 
 
def load_prev_data(pycrypto , connection) : 
    records = database.fetch_all_db_records("CryptoProfitDetector",connection)
    
    for record in records : 
        request_api(record[1])
        api=Api_Manager.get_api()
        while not Api_Manager.flag : api=Api_Manager.get_api()
        Api_Manager.reset_flag()
        currency_info = (api["data"][record[1]])[0]
        to_insert = perform_operations(entries_values = record[1:4] , currency_info=currency_info)
        insert_record(pycrypto , to_insert)
        Row_Index_Manager.increase_row_index()
        
     
        

def run() : 
    pycrypto = create_window()
    nb_of_headers = create_headers(pycrypto)
    generate_example(pycrypto)
    
    connection = database.start_connection("CoinMarketApi")
    database.create_table("CryptoProfitDetector" , connection , 
                          coin_name = "TEXT" ,
                          price_at_time_of_purchase = "REAL",
                          coin_owned = "INTEGER",
                          total_amount_paid="REAL",
                          price_at_this_moment="REAL",
                          current_value = "REAL",
                          profit_loss_per_coin="REAL", 
                          total_profit_loss_for_coin="REAL"
                          )
    

    load_prev_data(pycrypto , connection)
    
    
    create_button(pycrypto,nb_of_headers,connection)
    pycrypto.mainloop()
    

run()



# in database only store entries cuz others will get calculated at run time to keep up to data
# when internet connection is slow , the program goes crazy
# make a waiting window , so wehn you run the app


# currency not found error solve (THE PROBLEM WAS THAT INTERNET WAS SLOW SO API WAS BEING NONE UNTIL API DATA WAS GOT)
# oblige the user to enter first the currecny name OR make a way so that the program gets api before calculation occurs
# in api , pass the api_key as variable in params , cuz sometimes you will change the api_key


# add documentation for New.py and database.py