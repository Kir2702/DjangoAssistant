import main.generator.answer
import requests




def generating_response (order_id):

    def bo_data(order_id):
        order_id = str(order_id)
        headers = {"Authorization": ""}
        respons = requests.get('https://' + order_id, headers = headers, timeout=9)
        return respons


    def sj_data(order_id):
        data = {"orderid": order_id, "actionsearch": "/e/create"}
        headers = {"Authorization": ""}
        respons = requests.post('https://', headers = headers, json=data, timeout=9)
        return respons

    try:
        # получаем json из БО
        #bo_data = bo_data(order_id)
        # из этого json узнаем тип ответа всего 4 варианта
        #print(answer.test)
        #type = main.generator.answer.type(bo_data) # [undefined, booked, error, success]
        # получаем json из /e/create СЖ
        #sj_data = sj_data(order_id)
        type = 'undefined'
        
        # генерим ответ в зависимости от типа заказа
        if type == 'success':
            answer = main.generator.answer.success(bo_data, sj_data)
            return answer


        if type == 'error':
            answer = main.generator.answer.error(bo_data, sj_data)
            return answer


        if type == 'booked':
            answer = main.generator.answer.booked(bo_data, sj_data)
            return answer


        if type == 'undefined':
            return str("order type undefined")

    except requests.exceptions.ConnectTimeout:
        return str("Превышено время ожидания ответа от сервиса, попробуйте еще раз")


