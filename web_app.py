# -*- coding: utf-8 -*-
import sqlite3
from datetime import datetime, timedelta
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output


db_name = 'dnos.db'

conn = sqlite3.connect(db_name)
cur = conn.cursor()
cur.execute("""
       Select country, count(*) from user group by country;
               """)
list= cur.fetchall()
list= sorted(list, key=lambda x: x[1], reverse=True)
cur.close()
conn.close()


# Функция проверки, есть ли уже указанная страна(condition) в списке
def issu(list,condition):
 i =-1
 for j in list:
  i+=1
  if(list[i][0] == condition):
   return i
 return -1
 
def quest2(category):
 conn = sqlite3.connect(db_name)
 cur = conn.cursor()
 cur.execute("""
       Select user.country, user_info.ip from user INNER JOIN user_info
       ON user.ip = user_info.ip WHERE dejstvie = 'visit_category' AND category LIKE '{0}%' GROUP BY user.country, user_info.ip;
               """.format(category))
 list2= cur.fetchall()
 cur.close()
 conn.close()
 a = []
 i = -1
 for j in list2:
  i +=1
  k = issu(a,list2[i][0])
  if(k !=-1):
   a[k][1] = int(a[k][1]) + 1
  else: 
   a.append([list2[i][0],0])
 a = sorted(a, key=lambda x: x[1], reverse=True)
 return a;
 
def quest3(category):
 conn = sqlite3.connect(db_name)
 cur = conn.cursor()
 answer_pereods = []
 periods = {'night': ('00:00:00', '06:00:00'), 'morning': ('06:00:01','12:00:00'),
                'day': ('12:00:01', '18:00:00'), 'evening': ('18:00:01', '23:59:59')}
 for i in periods.keys():
  cur.execute("""
       SELECT COUNT(*) FROM user_info 
       WHERE dejstvie = 'visit_category' AND category LIKE '{0}%' AND
       time BETWEEN time("{1}") AND time("{2}");
               """.format(category, periods[i][0], periods[i][1]))
  list= cur.fetchall()
  answer_pereods.append(list[0][0])
 cur.close()
 conn.close()
 return answer_pereods
 
def quest4(date,time1,time2):
 conn = sqlite3.connect(db_name)
 cur = conn.cursor()
 
 cur.execute("""
       SELECT COUNT(*) FROM user_info 
       WHERE data = "{0}" AND time BETWEEN time("{1}") AND time("{2}");
               """.format(date, time1,time2))
 list4= cur.fetchall()
 cur.close()
 conn.close()
 return list4[0][0];
 
def quest6(time1,time2):
 conn = sqlite3.connect(db_name)
 cur = conn.cursor()
 cur.execute("""
       SELECT COUNT(*) FROM cart_info 
       WHERE pay = "no" and dats BETWEEN DATE("{0}") and DATE("{1}");
               """.format(time1,time2))
 list6 = cur.fetchall()
 cur.close()
 conn.close()
 return list6[0][0]


 
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}
app.layout = html.Div(children=[
    
     html.H1(children='Web визуализация отчётов парсера', style={
            'textAlign': 'center',
            
        }),
     html.H1(children='Задание №1', style={
            'textAlign': 'center',
            
        }),
     dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': [1], 'y': [list[0][1]], 'type': 'bar', 'name': list[0][0]},
                {'x': [2], 'y': [list[1][1]], 'type': 'bar', 'name': list[1][0]},
                {'x': [3], 'y': [list[2][1]], 'type': 'bar', 'name': list[2][0]},
                {'x': [4], 'y': [list[3][1]], 'type': 'bar', 'name': list[3][0]},
                {'x': [5], 'y': [list[4][1]], 'type': 'bar', 'name': list[4][0]},
            ],
            'layout': {
                'title': 'Посетители из какой страны совершают больше всего действий на сайте?'
            }
        }
       ),
 # SECTION 2   
    html.H1(children='''
        Задание №2
                      ''',style={
            'textAlign': 'center',
            
        }),
         html.Div(children='''Посетители из какой страны чаще всего интересуются товарами из определенных категорий?
                      ''', style={
            
            'font-size': '26px',
        }),
    html.Div(children='''
        Введите  категорию например semi_manufactures либо semi_manufactures/salmon_cutlet
                      ''', style={
            
            'font-size': '20px',
        }),
    dcc.Input(id='input-box', value='Введите категорию', type='text', style={ 'width': '900px',}),
    html.Button('Отправить', id='button', n_clicks=0),
    html.Div(id='slider-container'),
    
# SECTION 3
    
    html.H1(children='''
        Задание №3
                      ''',style={
            'textAlign': 'center',
            
        }),
    html.Div(children='''В какое время суток чаще всего просматривают определенную категорию товаров?
                      ''', style={
            
            'font-size': '26px',
        }),
    html.Div(children='''
        Введите  категорию например semi_manufactures либо semi_manufactures/salmon_cutlet
                      ''', style={
            
            'font-size': '20px',
        }),
    
    dcc.Input(id='input-box2', value='Введите категорию', type='text', style={ 'width': '900px',}),
    html.Button('Отправить', id='button2', n_clicks=0),
    html.Div(id='slider-container2'),
    
    # SECTION 4
    
    html.H1(children='''
        Задание №4
                      ''',style={
            'textAlign': 'center',
            
        }),
    html.Div(children='''Какая нагрузка (число запросов) на сайт за астрономический час?
                      ''', style={
            
            'font-size': '26px',
        }),
    html.Div(children='''
        Введите дату в формате YYYY-MM-DD. Пример 2018-08-01
                      ''', style={
            
            'font-size': '20px',
        }),
    
    dcc.Input(id='input-box-date', value='Введите дату', type='text', style={ 'width': '900px',}),
    html.Div(children='''
        Введите время начала отсчёта в формате HH:MI:SS. Пример 12:00:00
                      ''', style={
            
            'font-size': '20px',
        }),
    dcc.Input(id='input-box-time1', value='Введите время', type='text', style={ 'width': '900px',}),
        
        
    html.Div(children='''
        Введите время начала отсчёта в формате HH:MI:SS. Пример 16:00:00
                      ''', style={
            
            'font-size': '20px',
        }),
    dcc.Input(id='input-box-time2', value='Введите время', type='text', style={ 'width': '900px',}),
    html.Button('Отправить', id='button3', n_clicks=0),
    html.Div(id='slider-container3'),
    
    
 #SECTION 5
    html.H1(children='''
        Задание №6
                      ''',style={
            'textAlign': 'center',
            
        }),
    html.Div(children='''Сколько брошенных (не оплаченных) корзин имеется за определенный период?
                      ''', style={
            
            'font-size': '26px',
        }),
    dcc.Input(id='input-box-date1', value='Введите время начала отсчёта например 2018-08-01', type='text', style={ 'width': '900px',}),
    dcc.Input(id='input-box-date2', value='Введите время конца отсчёта например 2018-08-02', type='text', style={ 'width': '900px',}),
    html.Button('Отправить', id='button4', n_clicks=0),
    html.Div(id='slider-container4'),

    
])

# обработка событий 2-Й секции
@app.callback(Output('slider-container', 'children'), [Input('button', 'n_clicks')],
 [dash.dependencies.State('input-box', 'value')])
def on_click(n_clicks,input):
    list_question2 = quest2(input)
    if(len(list_question2)!=0):
     return html.Div(
        [dcc.Graph(
        id='example-graph2',
        figure={
            'data': [
                {'x': [1], 'y': [list_question2[0][1]], 'type': 'bar', 'name': list_question2[0][0]},
                {'x': [2], 'y': [list_question2[1][1]], 'type': 'bar', 'name': list_question2[1][0]},
                {'x': [3], 'y': [list_question2[2][1]], 'type': 'bar', 'name': list_question2[2][0]},
                {'x': [4], 'y': [list_question2[3][1]], 'type': 'bar', 'name': list_question2[3][0]},
                {'x': [5], 'y': [list_question2[4][1]], 'type': 'bar', 'name': list_question2[4][0]},
            ],
            'layout': {
                'title': 'Ответ на второй вопрос'
            }
        }
        )]+ 
        [html.Div(id='output-{}'.format(i)) for i in range(n_clicks)]
                   )
    else:
     return html.Div(html.Div(children='''
        Попробуйте ввести данные снова
                      ''', style={
            
            'font-size': '26px',
        }))


# обработка событий 3 секции
@app.callback(Output('slider-container2', 'children'), [Input('button2', 'n_clicks')],
 [dash.dependencies.State('input-box2', 'value')])
def on_click(n_clicks,input):
    list_question3 = quest3(input)
    if(list_question3[0]+list_question3[1]+list_question3[2]+list_question3[3]):
     return html.Div(
        [dcc.Graph(
        id='example-graph2',
        figure={
            'data': [
                {'x': [1], 'y': [list_question3[0]], 'type': 'bar', 'name': 'Ночь'},
                {'x': [2], 'y': [list_question3[1]], 'type': 'bar', 'name': 'Утро'},
                {'x': [3], 'y': [list_question3[2]], 'type': 'bar', 'name': 'День'},
                {'x': [4], 'y': [list_question3[3]], 'type': 'bar', 'name': 'Вечер'},
            ],
            'layout': {
                'title': 'Ответ на третий вопрос'
            }
        }
        )]+ 
        [html.Div(id='output-{}'.format(i)) for i in range(n_clicks)]
                   )
    else:
     return html.Div(html.Div(children='''
        Попробуйте ввести данные снова
                      ''', style={
            
            'font-size': '26px',
        }))
        
        
# обработка событий 4 секции       
@app.callback(Output('slider-container3', 'children'), [Input('button3', 'n_clicks')],
 [dash.dependencies.State('input-box-date', 'value'),
 dash.dependencies.State('input-box-time1', 'value'),
 dash.dependencies.State('input-box-time2', 'value')])
def on_click(n_clicks,input1,input2,input3):
    n = quest4(input1,input2,input3)
    if(n!=0):
     return html.Div(
        [dcc.Graph(
        id='example-graph2',
        figure={
            'data': [
                {'x': [1], 'y': [n], 'type': 'bar', 'name': 'Кол-во запросов'},
            ],
            'layout': {
                'title': 'Ответ на четвёртый вопрос'
            }
        }
        )]+ 
        [html.Div(id='output-{}'.format(i)) for i in range(n_clicks)]
                   )
    else:
     return html.Div(html.Div(children='''
        Попробуйте ввести данные снова
                      ''', style={
            
            'font-size': '26px',
        }))

@app.callback(Output('slider-container4', 'children'), [Input('button4', 'n_clicks')],
 [dash.dependencies.State('input-box-date1', 'value'),
 dash.dependencies.State('input-box-date2', 'value')])
def on_click(n_clicks,input1,input2):
    n = quest6(input1,input2)
    if(n!=0):
     return html.Div(
        [dcc.Graph(
        id='example-graph2',
        figure={
            'data': [
                {'x': [1], 'y': [n], 'type': 'bar', 'name': 'Кол-во брошенных корзин'},
            ],
            'layout': {
                'title': 'Ответ на шестой вопрос'
            }
        }
        )]+ 
        [html.Div(id='output-{}'.format(i)) for i in range(n_clicks)]
                   )
    else:
     return html.Div(html.Div(children='''
        Попробуйте ввести данные снова
                      ''', style={
            
            'font-size': '26px',
        }))


if __name__ == '__main__':
    
    app.run_server(debug=True)
    