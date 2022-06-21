import json
import datetime
import re


########[футкция формирования блока "заказ включает...."]##############################    
def order_includes(json):
    # получаем данные для формирования блока
    order_includes = {'railway_tickets': [], 'meal_blanks': [], 'baggage_blanks': [], 'insurance_blanks': []}
    for blank in json['blanks']:
        if blank['blank_type'] == 'ЖД-билеты':
            order_includes['railway_tickets'].append(blank['blank_number'])
        if blank['blank_type'] == 'ЖД, дополнительное питание':
            order_includes['meal_blanks'].append(blank['blank_number'])        
        if blank['blank_type'] == 'ЖД, дополнительный багаж':
            order_includes['baggage_blanks'].append(blank['blank_number'])
        if blank['blank_type'] == 'Страховки НС' or blank['blank_type'] == 'Страховки МС':
            order_includes['insurance_blanks'].append(blank['blank_number'])

    # формируем блок
    order_includ = str('')
    
    if len(order_includes['railway_tickets']) > 0:
        order_includ = (order_includ + 'Заказ включает ЭБ:')
        for ticket in order_includes['railway_tickets']:
            order_includ = (order_includ + ' № ' + str(ticket))
        order_includ = (order_includ + '\n')
          
    if len(order_includes['meal_blanks']) > 0:
        order_includ = (order_includ + 'Заказ включает ЭКРС:')
        for ticket in order_includes['meal_blanks']:
            order_includ = (order_includ + ' № ' + str(ticket))
        order_includ = (order_includ + '\n')
            
    if len(order_includes['baggage_blanks']) > 0:
        order_includ = (order_includ + 'Заказ включает ЭБК:')
        for ticket in order_includes['baggage_blanks']:
            order_includ = (order_includ + ' № ' + str(ticket))
        order_includ = (order_includ + '\n')
            
    if len(order_includes['insurance_blanks']) > 0:
        order_includ = (order_includ + 'Заказ включает ЭСП:')
        for ticket in order_includes['insurance_blanks']:
            order_includ = (order_includ + ' № ' + str(ticket))
        order_includ = (order_includ + '\n')
    return order_includ
    
######################################

def info_bloks(json):
    bliks_list1 = []
    # формируем список висех мршрутов, номеров поедов и дат отправлений
    for blank in json['blanks']:
        if blank['blank_type'] == 'ЖД-билеты':
            blok = []
            blok.append(blank['rout'])
            blok.append(blank['train_number'])
            blok.append(blank['departure_date_time'])
            bliks_list1.append(blok)

    # удаляем повторения из списка
    bliks_list = []
    for x in bliks_list1:
        if x not in bliks_list:
            bliks_list.append(x)
            
    # итоговая строка
    info_bloks = str('')

    # прописываем блоки
    for blok_element in bliks_list:
        info_bloks = (info_bloks + blok_element[0] + '\n')
        info_bloks = (info_bloks + 'Поезд: ' + blok_element[1] + '\n')
        info_bloks = (info_bloks + 'Отправление: ' + blok_element[2] + ' (местное)\n')
            
        # дописываем ЖД бланки    
        for blank in json['blanks']:
            if blank['blank_type'] == 'ЖД-билеты':
                if blok_element[0] == blank['rout'] and blok_element[1] == blank['train_number'] and blok_element[2] == blank['departure_date_time']:
                    info_bloks = (info_bloks + 'Статус ЭБ № ' + blank['blank_number'] + ':\n')
                    # дописываем допники к бланкам
                    for additional in json['blanks']:
                        if additional['blank_type'] != 'ЖД-билеты':
                            if blank['item_id'] == additional['main_item_id'] and blank['customers_id'] == additional['customers_id']:
                                    
                                if additional['blank_type'] == 'ЖД, дополнительное питание':
                                    info_bloks = (info_bloks + 'Статус ЭКРС № ' + additional['blank_number'] + ':\n')
                                      
                                if additional['blank_type'] == 'ЖД, дополнительный багаж':
                                    info_bloks = (info_bloks + 'Статус ЭБК № ' + additional['blank_number'] + ':\n')
                                        
                                if additional['blank_type'] == 'Страховки НС' or additional['blank_type'] == 'Страховки МС':
                                    info_bloks = (info_bloks + 'Статус ЭСП № ' + additional['blank_number'] + ':\n')
            
        info_bloks = (info_bloks + '\n')
                                    
    return info_bloks


######################################

def info_bloks_without_status (json):
    bliks_list1 = []
    # формируем список висех мршрутов, номеров поедов и дат отправлений
    for blank in json['blanks']:
        if blank['blank_type'] == 'ЖД-билеты':
            blok = []
            blok.append(blank['rout'])
            blok.append(blank['train_number'])
            blok.append(blank['departure_date_time'])
            bliks_list1.append(blok)

    # удаляем повторения из списка
    bliks_list = []
    for x in bliks_list1:
        if x not in bliks_list:
            bliks_list.append(x)

    # итоговая строка
    info_bloks = str('')

    # прописываем блоки
    for blok_element in bliks_list:
        info_bloks = (info_bloks + blok_element[0] + '\n')
        info_bloks = (info_bloks + 'Поезд: ' + blok_element[1] + '\n')
        info_bloks = (info_bloks + 'Отправление: ' + blok_element[2] + ' (местное)\n')
        info_bloks = (info_bloks + '\n')
    return info_bloks

                    
            



            
    

    
