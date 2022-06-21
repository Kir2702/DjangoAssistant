from jinja2 import Template
from . import adaptation
import re
import datetime
from json import loads



test = str('test')

########[функция определения типа ответа]#############################################################################################################
def type(bo_data):
    type = 'undefined' # значение типа ответа по умолчанию
    status_list=[]
    for l in bo_data.json():
        status_list.append(l.get("DisplayCssClass"))
    # убераем все повторяющиеся значения
    cash_list = []
    for i in status_list:
        cash_list.append(i)
    S = set()
    status_list = []
    for e in cash_list:
        if e in S:
            continue
        S.add(e)
        status_list.append(e)
    
    # определяем тип ответа
    if len(status_list) == 1:
        if status_list[0] == 'progress':
            type = 'booked'
        if status_list[0] == 'error':
            type = 'error'
        if status_list[0] == 'success':
            type = 'success'
    if len(status_list) > 1:
        if 'success' in status_list or 'return' in status_list:
            type = 'success'
    return type



######################################################################################################################################################

########[функция создания ответа по успешному шаблону]################################################################################################
def success_json(bo_data, sj_data):
    for l in sj_data.json():
        # получаем ID заказа
        orderidinjson = l.get("orderid")
        # получаем логин
        login = l.get("login")
        # получаем почту
        email = l.get("email")
        censorship = re.findall(r'(?<=\S)(\S+)[@]', email)
        if len(censorship) == 0:
            email_cens = re.findall(r'[@]\S+', email)
            email_cens = ('*' + email_cens[0])
        else:
            email_cens = re.sub(r'(?<=\S)(\S+)[@]', '*' * len(censorship[0]) + '@', email)
        # получение даты в Unix формате и перевод в читаемый вид
        date_time_create = l.get("datetime")
        date_time_create = re.findall(r'^\d\d\d\d\d\d\d\d\d\d', date_time_create)
        date_time_create = int((date_time_create[0]))
        date_time_create = datetime.datetime.fromtimestamp(date_time_create).strftime('%d.%m.%y' " в " '%H:%M')

    # создаем список бланков
    blanks = []

    for l in bo_data.json():
        # отсекаем только успешные
        if l.get("UiSimpleStatus") == 'Success':
            # отсекаем только покупки
            if l.get("DisplayType") == 'Покупка':
                # находим статус бланка
                blank_status = l.get("UiSimpleStatus")
                # находим тип бланка
                blank_type = l.get("DisplayServiceType")
                #
                main_item_id = l.get("MainItemId")
                # находим список основной информации по билету
                blanks_info = l.get("Blanks")
                #print(blanks_info) # отладка
                for blank_info in blanks_info:
                    # Cщздаем и заполняем  инфу по бланку
                    blank = {}
                    # номер бланка
                    blank_number = blank_info.get("BlankNumber")
                    # id для получения доп информации 
                    item_id = blank_info.get("OrderItemId")
                    # Получаем информацию по пассажирам
                    blank_customers = blank_info.get("BlankCustomers")
                    # IDшники пассажиров
                    customers_id = []
                    for customer in blank_customers:
                        customer_id = customer.get('OrderCustomerId')
                        customers_id.append(customer_id)
                    # записываем полученные данные поле blank
                    blank['item_id'] = item_id
                    blank['main_item_id'] = main_item_id
                    blank['blank_number'] = blank_number
                    blank['blank_type'] = blank_type
                    blank['blank_status'] = blank_status
                    blank['customers_id'] = customers_id
                    blanks.append(blank)
            
    for blank in blanks:
        # в уже готовом списке билетов нас интересуют только жд билеты
        if blank['blank_type'] == 'ЖД-билеты':
            # получаем id блока бланков из уже готового json
            json_item_id_blank = blank['item_id']
            for l in bo_data.json():
                # сравниваем значение item_id с тем же значением из данных БО
                if int(json_item_id_blank) == int(l.get("OrderItemId")):
                    # если сходятся лежем в блок с инфой по маршруту
                    route_parts = l.get("RouteParts")
                    for rout in route_parts:
                        if int(json_item_id_blank) == int(rout.get("OrderItemId")):
                            # получаем станцию отправления
                            origin_point = rout.get("OriginPoint").get("Name")
                            # получаем станцию прибытия
                            destination_point = rout.get("DestinationPoint").get("Name")
                            # собираем полный маршрут
                            full_rout = str(origin_point + " 🠖 " + destination_point)
                            # получаем номер поезда
                            train_number = rout.get("TripNumber")
                            # получаем дату отправления
                            departure_date_time = rout.get("Departure")
                            departure_date_time = re.sub(r'[T]', ' ', departure_date_time)
                            departure_time = re.findall(r'\d\d:\d\d:\d\d$', departure_date_time)
                            departure_year = re.findall(r'\d{4}', departure_date_time)
                            departure_year = re.findall(r'\d\d$', departure_year[0])
                            departure_month_day = re.findall(r'\b\d\d', departure_date_time)
                            departure_date_time = (departure_month_day[2] + '.' + departure_month_day[1] + '.' +  departure_year[0] + ' в ' +  departure_time[0])
                            departure_date_time = re.sub(r'\S\S\S$', '', departure_date_time)
                            # добавляем маршрут в список заказов
                            blank['rout'] = full_rout
                            # добавляем поезд в список заказов
                            blank['train_number'] = train_number
                            # добавляем дату отправления в список заказов
                            blank['departure_date_time'] = departure_date_time
    
    json = {
        'order_id': orderidinjson,  
        'login': login,
        'email': email_cens,
        'date_time_create': date_time_create,
        'blanks': blanks
        }
    return json


########[функция обработки данных для шаблона]##################################################
def success_adaptation(json):
    #футкция формирования блока "заказ включает...."
    order_includes = adaptation.order_includes(json)
    info_bloks = adaptation.info_bloks(json)
    json['order_includes'] = order_includes
    json['info_bloks'] = info_bloks
    return json

########[функция добавления данныз в шаблон]##################################################
def success_template(json):
    with open("main/generator/success.txt", "r", encoding="utf-8") as template:
        read_template = template.read()
    read_template = Template(read_template, trim_blocks = True)
    answer = read_template.render(json)
    return answer

#################################################################################
def success(bo_data, sj_data):
    #Получаем данные для шаблона
    json = success_json(bo_data, sj_data)
    # обрабатывает json
    json = success_adaptation(json)
    #заполняем шаблон
    answer = success_template(json)
    return answer

######################################################################################################################################################
######################################################################################################################################################
########[функция создания ответа по шаблону ошибки]################################################################################################
def error_json(bo_data, sj_data):
    for l in sj_data.json():
        # получаем ID заказа
        orderidinjson = l.get("orderid")
        # получаем логин
        login = l.get("login")
        # получаем почту
        email = l.get("email")
        censorship = re.findall(r'(?<=\S)(\S+)[@]', email)
        if len(censorship) == 0:
            email_cens = re.findall(r'[@]\S+', email)
            email_cens = ('*' + email_cens[0])
        else:
            email_cens = re.sub(r'(?<=\S)(\S+)[@]', '*' * len(censorship[0]) + '@', email)
        # получение даты в Unix формате и перевод в читаемый вид
        date_time_create = l.get("datetime")
        date_time_create = re.findall(r'^\d\d\d\d\d\d\d\d\d\d', date_time_create)
        date_time_create = int((date_time_create[0]))
        date_time_create = datetime.datetime.fromtimestamp(date_time_create).strftime('%d.%m.%y' " в " '%H:%M')
        # получаем ID платежа
        response = l.get('response')
        response = loads(response)
        agent_payment_id = response['AgentPaymentId']



    # создаем список бланков
    blanks = []
    for l in bo_data.json():
        print(l.get("UiSimpleStatus"))
        # отсекаем только успешные
        if l.get("UiSimpleStatus") == 'Error':
            # отсекаем только покупки
            if l.get("DisplayType") == 'Покупка':
                # находим статус бланка
                blank_status = l.get("UiSimpleStatus")
                # находим тип бланка
                blank_type = l.get("DisplayServiceType")
                print(blank_type)
                #
                main_item_id = l.get("MainItemId")
                # находим список основной информации по билету
                blanks_info = l.get("Blanks")
                # print(blanks_info) # отладка
                for blank_info in blanks_info:
                    # Cщздаем и заполняем  инфу по бланку
                    blank = {}
                    # номер бланка
                    blank_number = blank_info.get("BlankNumber")
                    # id для получения доп информации
                    item_id = blank_info.get("OrderItemId")
                    # Получаем информацию по пассажирам
                    blank_customers = blank_info.get("BlankCustomers")
                    # IDшники пассажиров
                    customers_id = []
                    for customer in blank_customers:
                        customer_id = customer.get('OrderCustomerId')
                        customers_id.append(customer_id)
                    # записываем полученные данные поле blank
                    blank['item_id'] = item_id
                    blank['main_item_id'] = main_item_id
                    blank['blank_number'] = blank_number
                    blank['blank_type'] = blank_type
                    blank['blank_status'] = blank_status
                    blank['customers_id'] = customers_id
                    blanks.append(blank)
    for blank in blanks:
        # в уже готовом списке билетов нас интересуют только жд билеты
        if blank['blank_type'] == 'ЖД-билеты':
            # получаем id блока бланков из уже готового json
            json_item_id_blank = blank['item_id']
            for l in bo_data.json():
                # сравниваем значение item_id с тем же значением из данных БО
                if int(json_item_id_blank) == int(l.get("OrderItemId")):
                    # если сходятся лежем в блок с инфой по маршруту
                    route_parts = l.get("RouteParts")
                    for rout in route_parts:
                        if int(json_item_id_blank) == int(rout.get("OrderItemId")):
                            # получаем станцию отправления
                            origin_point = rout.get("OriginPoint").get("Name")
                            # получаем станцию прибытия
                            destination_point = rout.get("DestinationPoint").get("Name")
                            # собираем полный маршрут
                            full_rout = str(origin_point + " 🠖 " + destination_point)
                            # получаем номер поезда
                            train_number = rout.get("TripNumber")
                            # получаем дату отправления
                            departure_date_time = rout.get("Departure")
                            departure_date_time = re.sub(r'[T]', ' ', departure_date_time)
                            departure_time = re.findall(r'\d\d:\d\d:\d\d$', departure_date_time)
                            departure_year = re.findall(r'\d{4}', departure_date_time)
                            departure_year = re.findall(r'\d\d$', departure_year[0])
                            departure_month_day = re.findall(r'\b\d\d', departure_date_time)
                            departure_date_time = (
                                        departure_month_day[2] + '.' + departure_month_day[1] + '.' + departure_year[
                                    0] + ' в ' + departure_time[0])
                            departure_date_time = re.sub(r'\S\S\S$', '', departure_date_time)
                            # добавляем маршрут в список заказов
                            blank['rout'] = full_rout
                            # добавляем поезд в список заказов
                            blank['train_number'] = train_number
                            # добавляем дату отправления в список заказов
                            blank['departure_date_time'] = departure_date_time

    json = {
        'order_id': orderidinjson,
        'login': login,
        'email': email_cens,
        'date_time_create': date_time_create,
        'agent_payment_id': agent_payment_id,
        'blanks': blanks
    }
    return json


########[функция обработки данных для шаблона]##################################################
def error_adaptation(json):
    # футкция формирования блока "заказ включает...."
    order_includes = adaptation.order_includes(json)
    info_bloks_without_status = adaptation.info_bloks_without_status(json)
    json['info_bloks_without_status '] = info_bloks_without_status
    return json


########[функция добавления данныз в шаблон]##################################################
def error_template(json):
    with open("main/generator/error.txt", "r", encoding="utf-8") as template:
        read_template = template.read()
    read_template = Template(read_template, trim_blocks=True)
    answer = read_template.render(json)
    return answer


#################################################################################
def error(bo_data, sj_data):
    # Получаем данные для шаблона
    json = error_json(bo_data, sj_data)
    # обрабатывает json
    print(json)
    json = error_adaptation(json)
    # заполняем шаблон
    answer = error_template(json)
    return answer

######################################################################################################################################################
######################################################################################################################################################
########[функция создания ответа по успешному шаблону]################################################################################################
def booked_json(bo_data, sj_data):
    for l in sj_data.json():
        # получаем ID заказа
        orderidinjson = l.get("orderid")
        # получаем логин
        login = l.get("login")
        # получаем почту
        email = l.get("email")
        censorship = re.findall(r'(?<=\S)(\S+)[@]', email)
        if len(censorship) == 0:
            email_cens = re.findall(r'[@]\S+', email)
            email_cens = ('*' + email_cens[0])
        else:
            email_cens = re.sub(r'(?<=\S)(\S+)[@]', '*' * len(censorship[0]) + '@', email)
        # получение даты в Unix формате и перевод в читаемый вид
        date_time_create = l.get("datetime")
        date_time_create = re.findall(r'^\d\d\d\d\d\d\d\d\d\d', date_time_create)
        date_time_create = int((date_time_create[0]))
        date_time_create = datetime.datetime.fromtimestamp(date_time_create).strftime('%d.%m.%y' " в " '%H:%M')

    # создаем список бланков
    blanks = []

    for l in bo_data.json():
        # отсекаем только успешные
        if l.get("UiSimpleStatus") == 'InProgress':
            # отсекаем только покупки
            if l.get("DisplayType") == 'Покупка':
                # находим статус бланка
                blank_status = l.get("UiSimpleStatus")
                # находим тип бланка
                blank_type = l.get("DisplayServiceType")
                #
                main_item_id = l.get("MainItemId")
                # находим список основной информации по билету
                blanks_info = l.get("Blanks")
                # print(blanks_info) # отладка
                for blank_info in blanks_info:
                    # Cщздаем и заполняем  инфу по бланку
                    blank = {}
                    # номер бланка
                    blank_number = blank_info.get("BlankNumber")
                    # id для получения доп информации
                    item_id = blank_info.get("OrderItemId")
                    # Получаем информацию по пассажирам
                    blank_customers = blank_info.get("BlankCustomers")
                    # IDшники пассажиров
                    customers_id = []
                    for customer in blank_customers:
                        customer_id = customer.get('OrderCustomerId')
                        customers_id.append(customer_id)
                    # записываем полученные данные поле blank
                    blank['item_id'] = item_id
                    blank['main_item_id'] = main_item_id
                    blank['blank_number'] = blank_number
                    blank['blank_type'] = blank_type
                    blank['blank_status'] = blank_status
                    blank['customers_id'] = customers_id
                    blanks.append(blank)

    for blank in blanks:
        # в уже готовом списке билетов нас интересуют только жд билеты
        if blank['blank_type'] == 'ЖД-билеты':
            # получаем id блока бланков из уже готового json
            json_item_id_blank = blank['item_id']
            for l in bo_data.json():
                # сравниваем значение item_id с тем же значением из данных БО
                if int(json_item_id_blank) == int(l.get("OrderItemId")):
                    # если сходятся лежем в блок с инфой по маршруту
                    route_parts = l.get("RouteParts")
                    for rout in route_parts:
                        if int(json_item_id_blank) == int(rout.get("OrderItemId")):
                            # получаем станцию отправления
                            origin_point = rout.get("OriginPoint").get("Name")
                            # получаем станцию прибытия
                            destination_point = rout.get("DestinationPoint").get("Name")
                            # собираем полный маршрут
                            full_rout = str(origin_point + " 🠖 " + destination_point)
                            # получаем номер поезда
                            train_number = rout.get("TripNumber")
                            # получаем дату отправления
                            departure_date_time = rout.get("Departure")
                            departure_date_time = re.sub(r'[T]', ' ', departure_date_time)
                            departure_time = re.findall(r'\d\d:\d\d:\d\d$', departure_date_time)
                            departure_year = re.findall(r'\d{4}', departure_date_time)
                            departure_year = re.findall(r'\d\d$', departure_year[0])
                            departure_month_day = re.findall(r'\b\d\d', departure_date_time)
                            departure_date_time = (
                                        departure_month_day[2] + '.' + departure_month_day[1] + '.' + departure_year[
                                    0] + ' в ' + departure_time[0])
                            departure_date_time = re.sub(r'\S\S\S$', '', departure_date_time)
                            # добавляем маршрут в список заказов
                            blank['rout'] = full_rout
                            # добавляем поезд в список заказов
                            blank['train_number'] = train_number
                            # добавляем дату отправления в список заказов
                            blank['departure_date_time'] = departure_date_time

    json = {
        'order_id': orderidinjson,
        'login': login,
        'email': email_cens,
        'date_time_create': date_time_create,
        'blanks': blanks
    }
    return json


########[функция обработки данных для шаблона]##################################################
def booked_adaptation(json):
    return json


########[функция добавления данныз в шаблон]##################################################
def booked_template(json):
    with open("main/generator/booked.txt", "r", encoding="utf-8") as template:
        read_template = template.read()
    read_template = Template(read_template, trim_blocks=True)
    answer = read_template.render(json)
    return answer


#################################################################################
def booked(bo_data, sj_data):
    # Получаем данные для шаблона
    json = booked_json(bo_data, sj_data)
    # обрабатывает json
    json = booked_adaptation(json)
    # заполняем шаблон
    answer = booked_template(json)
    return answer
    
