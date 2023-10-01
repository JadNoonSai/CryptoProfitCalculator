from tkinter import *
from tkinter import messagebox,ttk
from tkmacosx import Button as macButton
import json,requests,threading,database,datetime,time,concurrent.futures,queue,os,sys
from PIL import ImageTk , Image

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
    pycrypto.resizable(False,False)
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

def get_supported_currencies() :
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/map?CMC_PRO_API_KEY=f63ff251-a883-4b92-8a3d-2685615e31bf"
    api_request = requests.get(url)
    api_got:dict = json.loads(api_request.content)
    supported_currencies = api_got["data"]
    supported_currencies = [(dictionary["symbol"],) for dictionary in supported_currencies]
    return supported_currencies

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
    button.grid(row=Row_Index_Manager.row_index,column=0,columnspan = nb_of_headers , sticky=N+S+W+E)


def create_entries(pycrypto) : 
    entries = []
    for i in range(3) :
        entry = Entry(pycrypto , relief="groove" ,bd=2,bg="white",fg="black")
        entry.grid(row=Row_Index_Manager.row_index , column = i+1 ,sticky=N+S+W+E)
        entries.append(entry)
    
    return entries


def create_calculate_button(pycrypto , entries , nb_of_headers,connection) : 
    calculate_button = macButton(pycrypto,text = "Calculate",bg="#ff3300", command =lambda :  my_portfolio(pycrypto,entries,calculate_button,nb_of_headers,connection))
    calculate_button.grid(row=Row_Index_Manager.row_index,column = 4 , columnspan = nb_of_headers-3,sticky = N+S+E+W)

def create_record(pycrypto , button , nb_of_headers,connection) :

    button.destroy()

    entries = create_entries(pycrypto)
    entries[0].bind("<KeyRelease>" , lambda event , symbol_entry=entries[0]: request_api(symbol_entry.get().upper()))

    create_calculate_button(pycrypto , entries , nb_of_headers , connection)
    

def get_api_error_port(rt:requests.exceptions.ReadTimeout):
    error_string =str(rt.args[0])
    index = error_string.find("port=")
    port = error_string[index:index+8]
    return port


def request_api(symbol) :
    
    key = "f63ff251-a883-4b92-8a3d-2685615e31bf"
    url = f'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'
    params = {'symbol': symbol , 'CMC_PRO_API_KEY' : key}

    def make_request():

        try : api_request = requests.get(url, params=params,timeout=15)
        except requests.exceptions.ReadTimeout as rt :
            port = get_api_error_port(rt)
            if messagebox.askretrycancel("Server Error",f"Server Error : {port}") :
                request_api(symbol)
                return
        except :
            if messagebox.askretrycancel("Network Connection Problem","No Intenet Connection") :
                request_api(symbol)
                return

        else:
            api_got:dict = json.loads(api_request.content)
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


def create_label_after_calculation(pycrypto,to_insert,font_color,i):
    label = Label(pycrypto , text = str(to_insert[i]).upper() , relief =GROOVE , bd=2 ,fg = font_color,bg="white")
    label.grid(row=Row_Index_Manager.row_index , column = i , sticky = N+S+E+W)
    return label
    


def create_delete_button(pycrypto , labels , connection,id) : 
    del_button= macButton(pycrypto,text=id, width=40 , command = lambda : delete_record(id,del_button,labels,connection))
    del_button.grid(row=Row_Index_Manager.row_index,column = 0,sticky=N+S+E+W)
    del_button.bind("<Enter>", lambda event , del_button=del_button : del_button.configure(text="-" , fg="red",font= "Lato 16 "))
    del_button.bind("<Leave>", lambda event , del_button=del_button : del_button.configure(text=id , fg="black",font="Lato 13"))

    
def insert_record(pycrypto,to_insert,connection):

    labels=[]
    for i in range(1,len(to_insert)) :
        if get_headers()[i]=="P/L Per Coin" or get_headers()[i]=="Total P/L With Coin":
            font_color = get_font_color(float(to_insert[i]))
        else : font_color = "black"
        label = create_label_after_calculation(pycrypto,to_insert,font_color,i)
        labels.append(label)
        
    id = to_insert[0]
    create_delete_button(pycrypto,labels , connection , id)



def delete_record(id,del_button,labels,connection) :
    database.delete_record("CryptoProfitDetectorNew",id,connection)
    del_button.destroy()
    for label in labels : label.destroy()


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


def is_valid_currency(symbol,connection):
    records = database.fetch_all_db_records("SupportedCurrencies",connection)
    for record in records :
        if record[1]==symbol : return True
    return False

def record_exists_protocol(pycrypto , calculate_button , entries , nb_of_headers , connection):
    messagebox.showerror("Adding New Record" , "Record Already Exists")
    calculate_button.destroy()
    destroy_entries(entries)
    create_button(pycrypto,nb_of_headers,connection)

    

def my_portfolio(pycrypto,entries,calculate_button,nb_of_headers,connection,retries = 1) :

    entries = check_entries(entries)
    if not entries:return

    entries_values = [entry.get().upper() for entry in entries]

    if not is_valid_currency(entries_values[0],connection) :
        write_error(entries[0] , "No Such Currency")
        return


    exists = database.record_already_exists("CryptoProfitDetectorNew",connection,entries_values)
    if exists :
        record_exists_protocol(pycrypto,calculate_button,entries , nb_of_headers,connection)
        return

    calculate_button.config(text = "Slow Internet Connection , one sec" , fg = "white" , bg ="#142E54")
    # Force GUI update
    calculate_button.update_idletasks()

    symbol = entries_values[0]

    api = Api_Manager.get_api()

    #Instead i simply put timeout for requests module , so if time is passed , i think api would be None
    # so we say while not api : Api_Manager:
    try : currency_info = (api["data"][symbol])[0]
    except Exception as e:
        if retries == 0:
            if messagebox.askretrycancel("Add Record" , "Slow Internet Connection") :
                calculate_button.config(text = "Retrying" , fg = "white" , bg ="#ff3300")
                # Force GUI update
                calculate_button.update_idletasks()
                my_portfolio(pycrypto, entries, calculate_button, nb_of_headers, connection, retries=1)
                return

            else :
                calculate_button.config(text = "Calculate" , fg = "white" , bg ="#ff3300")
                # Force GUI update
                calculate_button.update_idletasks()
                return

        retries -= 1
        request_api(entries_values[0])
        time.sleep(5)# Sleep for 10 seconds before retrying
        my_portfolio(pycrypto, entries, calculate_button, nb_of_headers, connection, retries)
        return
        # return my_portfolio(pycrypto , entries , calculate_button,nb_of_headers,connection,retries) why it is never executed


    calculate_button.config(text = "Calculate" , bg ="#ff3300")
    to_insert = perform_operations(entries_values , currency_info)
    database.insert_db_record("CryptoProfitDetectorNew", connection , tuple(entries_values)   )

    calculate_button.destroy()
    destroy_entries(entries)
    insert_record(pycrypto,to_insert,connection)


    Row_Index_Manager.increase_row_index()
    create_button(pycrypto,nb_of_headers,connection)




def load_prev_data(progress_queue,connection) :
    records = database.fetch_all_db_records("CryptoProfitDetectorNew",connection)
    to_insert_list = []

    if not records :
        progress_queue.put("No Records")
        return

    progress_bar_increment_rate = 100/len(records)

    Row_Index_Manager.row_index=2

    for record in records :
        request_api(record[1])
        api=Api_Manager.get_api()
        while not Api_Manager.flag : api=Api_Manager.get_api()
        Api_Manager.reset_flag()
        try : currency_info = (api["data"][record[1]])[0]
        except :
            time.sleep(3)
            api=Api_Manager.get_api()
            while not Api_Manager.flag : api=Api_Manager.get_api()
            Api_Manager.reset_flag()
        to_insert = perform_operations(entries_values = record[1:] , currency_info=currency_info)
        progress_queue.put(progress_bar_increment_rate)
        to_insert_list.append(to_insert)
        Row_Index_Manager.increase_row_index()


    progress_queue.put(to_insert_list)


'''
def stay_up_to_date(pycrypto,connection,nb_of_headers):
    start = datetime.datetime.now()

    delta = (datetime.datetime.now() - start).total_seconds()
    if int(delta) == 10 :
        messagebox.showinfo(message="Data Updated")
        records = database.fetch_all_db_records("CryptoProfitDetectorNew",connection)
        database.delete_all_records("CryptoProfitDetectorNew",connection)
        database.insert_many_db_records("CryptoProfitDetectorNew",connection,records)

        for i,widget in enumerate(pycrypto.winfo_children()) :
            if type(widget) == Label and i>=nb_of_headers :
                widget.destroy()

        to_insert_list = load_prev_data(pycrypto,connection)
        for record in to_insert_list :
            insert_record(pycrypto , record,connection)
            Row_Index_Manager.increase_row_index()

    pycrypto.after(100,lambda : stay_up_to_date(pycrypto,connection,nb_of_headers))'''


def check_queue(progress_queue,progress_bar,pycrypto,canvas,connection,progress_bar_id,text_id) :
    try :
        msg = progress_queue.get(0)
        if msg=="No Records":
            canvas.delete(text_id)
            canvas.delete(progress_bar_id)
            Launch_Button(pycrypto,canvas,connection,[])

        elif type(msg)==list:

            canvas.delete(text_id)
            canvas.delete(progress_bar_id)
            Launch_Button(pycrypto,canvas,connection,msg)

        else :
            progress_bar["value"]+=msg
            canvas.itemconfig(text_id,text=f"Keeping Data Up to Date , loading...  {progress_bar['value']:.1f}%")
            progress_bar.after(100,lambda : check_queue(progress_queue,progress_bar,pycrypto,canvas,connection,progress_bar_id,text_id))

    except queue.Empty: progress_bar.after(100,lambda : check_queue(progress_queue,progress_bar,pycrypto,canvas,connection,progress_bar_id,text_id))




#e78332
def Launch_Button(pycrypto,canvas,connection,to_insert_list) :
    launch_button = macButton(pycrypto,text ="Launch",relief=FLAT,command = lambda :open_app(pycrypto,connection,to_insert_list) )
    launch_button.bind("<Enter>" , lambda event: launch_button.configure(bg="#efc444",font="Lato 15",fg="white"))
    launch_button.bind("<Leave>" , lambda event: launch_button.configure(bg="white",font="Lato 13",fg="black"))
    canvas.create_window(pycrypto.winfo_width()//2 , pycrypto.winfo_height()//2,window=launch_button)
    return launch_button


# This is necessary cuz bg_image.png must be in "temporary" folder so that .app can make use of it
def add_bg_image_to_temp_folder():
    # Get the absolute path of the temporary folder
    bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))

    # Join the temporary folder with the relative path of the data file
    path_to_image = os.path.abspath(os.path.join(bundle_dir, 'bg_image.png'))
    return path_to_image


def background_image(pycrypto):
      

    # path_to_image = add_bg_image_to_temp_folder()
    path_to_image = 'bg_image.png'
    pycrypto.update_idletasks()
    window_width,window_height = pycrypto.winfo_width(),pycrypto.winfo_height()

    bg_image = Image.open(path_to_image)
    bg_image = bg_image.resize((window_width, window_height))
    pycrypto.bg_image = ImageTk.PhotoImage(bg_image)
    canvas = Canvas(pycrypto,width=window_width,height=window_height)
    canvas.create_image(window_width//2,window_height//2,anchor=CENTER, image =pycrypto.bg_image)
    return canvas




    


def run() :
    pycrypto = create_window()
    pycrypto.geometry("700x600")
    canvas = background_image(pycrypto)
    canvas.grid()
    
    
    
    # db_tables_thread = threading.Thread(target = create_db_tables , args = [connection])
    # db_tables_thread.start()

    progress_bar = ttk.Progressbar(pycrypto,orient="horizontal",length=200,mode="determinate")
    text_id = canvas.create_text(pycrypto.winfo_width()//2 , (pycrypto.winfo_height()//2)+30,text="loading...  0%")
    canvas.itemconfig(text_id,fill="white")
    progress_bar_id = canvas.create_window(pycrypto.winfo_width()//2 , pycrypto.winfo_height()//2,window=progress_bar)
    pycrypto.update_idletasks()
    
    
    connection = database.start_connection("CoinMarketApi")
    database.create_table("CryptoProfitDetectorNew" , connection ,
                          coin_name = "TEXT" ,
                          price_at_time_of_purchase = "REAL",
                          coin_owned = "INTEGER"
                          )
    
    database.create_table("SupportedCurrencies",connection , symbol = "TEXT" )      
    database.insert_many_db_records_supported_currencies("SupportedCurrencies",connection,get_supported_currencies())
    
    # database.delete_all_records("CryptoProfitDetectorNew",connection)
    progress_queue= queue.Queue()
    
    
    # db_tables_thread.join()
    thread = threading.Thread(target= load_prev_data,args=[progress_queue,connection])
    thread.start()
    check_queue(progress_queue,progress_bar,pycrypto,canvas,connection,progress_bar_id,text_id)



    pycrypto.mainloop()



def open_app(pycrypto,connection,to_insert_list ):

    pycrypto.destroy()

    Row_Index_Manager.row_index = 0

    pycrypto = create_window()


    nb_of_headers = create_headers(pycrypto)
    generate_example(pycrypto)


    for record in to_insert_list :
        insert_record(pycrypto , record,connection)
        Row_Index_Manager.increase_row_index()


    create_button(pycrypto,nb_of_headers,connection)



run()


# make pycrypot resizable  so that when you resize the window , the image automatically fits in,
#   and make the window when records are listed be filled the rest with the image

'''modify the prog so that :
    1_ if there is not internet conenction when running the program,it informs the user
    2_ it deals with the case that if there were internet connection and WHILE launching the program,
    the internet connection goes , the app knows that and infroms the user'''


# make load records fast using threads
# make wait window at run of program


# change name of table CryptoProfitDetectorNew to CryptoProfitDetector
# app depends on internet , so if there is no internet when trying to open hte app,
#pop up a message that says Internet is Needed



'''modify the prog so that : 
    1_ if there is not internet conenction when running the program,it informs the user
    2_ it deals with the case that if there were internet connection and WHILE launching the program,
    the internet connection goes , the app knows that and infroms the user'''
 

# make load records fast using threads
# make wait window at run of program


# change name of table CryptoProfitDetectorNew to CryptoProfitDetector
# app depends on internet , so if there is no internet when trying to open hte app,
#pop up a message that says Internet is Needed





 # ran  only once to store in database the supported currencies 
    # database.create_table("SupportedCurrencies",connection , symbol = "TEXT" )      
    # database.insert_many_db_records_supported_currencies("SupportedCurrencies",connection,get_supported_currencies())
    
