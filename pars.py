import sqlite3
import re
import urllib.request
from datetime import datetime, timedelta

db_name = 'dnos.db'

conn = sqlite3.connect(db_name)
cur = conn.cursor()

# Узнавать страны будем по api запросам от сайта
ip_server_country = 'http://api.wipmania.com/'


#  Таблица содержащая пару ip и соответствующая страна 
user_info_table = 'user';
user_ip = 'ip'
user_country = 'country'

#  Таблица содержащая информацию о действиях пользователя
user_log_table = 'user_info';
user_log_ip = 'ip';
user_log_data= 'data'
user_log_time= 'time'
user_log_category = 'category'
user_log_do = 'dejstvie'

# Таблица содержащая информацию о корзинах
cart_table = 'cart_info';
cart_ip = 'ip';
cart_time= 'time'
cart_date= 'dats'
cart_id = 'cart'
cart_pay = 'pay' #Оплачена ли корзина 


#Функция получения страны по ip
def ip_country(ip):
 response = urllib.request.urlopen(ip_server_country + ip)
 country = response.read()
 return country.decode('utf-8')

# Функция проверки на наличие ip(записи) в таблице
def is_ip_exist(ip, tablename, column):
        cur.execute("""
        SELECT {0} FROM {1} WHERE {2} = (?);
        """.format(column, tablename, column), (ip,))
        is_exist = cur.fetchone()
        if is_exist is None:
            return False
        else:
            return True
# Функция для обработки ссылки(url)            
def parse_url(url):
        # Посещение стартовой страницы
        main_page = 'visit_main'
        # Посещение категории
        category = 'visit_category'
        # Добавление товара в корзину
        add_goods_to_cart = 'add_to_cart'
        # Попытка оплаты
        try_to_pay = 'to_pay'
        # Успешная оплата
        success= 'success_pay'

        cat = []
        cat_url = re.split('.*?//.*?/', url)
        cat_url = cat_url[1].strip('/\n')
        if cat_url == '':
            cat.append(main_page)
            cat.append('/')
        elif (cat_url.replace('_', '').isalpha()) or ('/' in cat_url):         
            cat.append(category)
            cat.append(cat_url)
        elif 'goods' in cat_url:
            temp = []
            cat.append(add_goods_to_cart)
            digits = re.findall('\d+', cat_url)
            for num in digits:
                temp.append(int(num))
            cat.append(cat_url)
            cat.append(temp[2])
        elif 'pay?user' in cat_url:
            cat.append(try_to_pay)
            cat.append(cat_url)
        elif 'success' in cat_url:
            cat.append(success)
            success_pay = re.findall('\d+', cat_url)
            cat.append(url[29:])
            cat.append(success_pay[0])            
        else:
            raise Exception
        return cat

# Добавление записи в таблицу где содержится (ip,country)
def add_to_ip(ip):
 if( is_ip_exist(ip, user_info_table, user_ip)== False):
  country_name = ip_country(ip);
  cur.execute("""
        INSERT INTO {0}({1},{2}) VALUES (?, ?);
        """.format(user_info_table, user_ip, user_country), (ip, str(country_name)))
  conn.commit()
 # Добавление записи во вторую таблицу
def add_to_info_users(list):

 if(list[3]=='add_to_cart'):
  cur.execute("""
        INSERT INTO {0}({1},{2},{3},{4}) VALUES (?, ?, ?, ?);
        """.format(cart_table, cart_ip,cart_date,cart_time,cart_id), (list[2],list[0],list[1],list[5]))
 if(list[3]=='success_pay'):
  if(is_ip_exist(list[5],cart_table,cart_id)==True):
   cur.execute("""
        UPDATE {0} SET {1} = 'yes' WHERE {2} = {3};
        """.format(cart_table, cart_pay,cart_id,str(list[5])))
#######
 cur.execute("""
        INSERT INTO {0}({1},{2},{3},{4},{5}) VALUES (?, ?, ?, ?, ?);
        """.format(
        user_log_table,
        user_log_ip,
        user_log_category,
        user_log_do, 
        user_log_time,
        user_log_data),(list[2],list[4],list[3],list[1],list[0]))
   
  
def parse_line(line):
        delit = [5, 4, 1, 0]
        line_list = re.split('\ +', line)
        
        for i in delit:
            del line_list[i]
        url = line_list.pop()
        # Парсинг url строки
        for elem in parse_url(url):
            if elem != '':
                line_list.append(elem)
     
        return line_list
        
#Функция заполнения БД        
def filling_database(f_name):
        with open(f_name, 'r') as f:
            line = f.readline()
            while line:
                parsed_line = parse_line(line)
                print(parsed_line)
                add_to_ip(parsed_line[2])
                add_to_info_users(parsed_line)
                line = f.readline()
                
# Функция для создания таблиц изначально                
def create_tables():
 cur.execute("""
                        CREATE TABLE IF NOT EXISTS {0} (
                        {1} integer PRIMARY KEY,
                        {2} text,
                        {3} text
                        );
        """.format(user_info_table,"id","ip" ,"country" ))

 cur.execute("""
                        CREATE TABLE IF NOT EXISTS {0} (
                        {1} integer PRIMARY KEY,
                        {2} text,
                        {3} text,
                        {4} text,
                        {5} TIME,
                        {6} DATE
                        );
        """.format(user_log_table,"id",user_log_ip ,user_log_category ,user_log_do, user_log_time,user_log_data))

 cur.execute("""
                        CREATE TABLE IF NOT EXISTS {0} (
                        {1} integer,
                        {2} text,
                        {3} text,
                        {4} text,
                        {5} text DEFAULT 'no'
                        );
        """.format(cart_table,cart_ip,cart_date,cart_time,cart_id,cart_pay))


if __name__ == '__main__':
 
 create_tables()

 filling_database("logs_2.0.txt")
 
 cur.close()
 conn.close()
 
 
 
 
 
 
 