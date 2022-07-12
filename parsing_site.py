
import requests
import json
from bs4 import BeautifulSoup

headers = {
    "Authorization": "Bearer gtcwf654agufy25gsadh"
}

proxies = {
    'https': 'https://91.246.103.106:3128'
}

# proxies = []

def check_proxy():
    for proxy in proxies:
        try:
            response = requests.get('http://icanhazip.com/', headers={"Authorization": "Bearer gtcwf654agufy25gsadh"}, proxies={
                'https': f"https://{proxy}"
                })
        except:
            continue
        print(proxy)




def get_barbers():
    response = requests.get('https://b70280.alteg.io/api/v1/book_staff/86104', headers=headers)
    list_barbers = json.loads(response.content)

    actual_barbers = {}

    for barber_data in list_barbers:
        if barber_data.get('bookable'):
            actual_barbers[barber_data.get('name')] = {
                'id_barber': barber_data.get('id'),
                'name': barber_data.get('name'),
                'specialization':barber_data.get('specialization'),
                'avatar': barber_data.get('avatar_big')
            }
    print(*actual_barbers)
    return actual_barbers

def get_bookingday(id_barber):

    params = {
        'staff_id': id_barber,
    }

    response = requests.get("https://b70280.alteg.io/api/v1/book_dates/86104", params=params, headers=headers)

    result = response.json()
    return result.get('booking_dates')

def get_bookingtime(id_barber, date_booking):

    response = requests.get(f"https://b70280.alteg.io/api/v1/book_times/86104/{id_barber}/{date_booking}", headers=headers)

    result = response.json()
    return result


def get_bookingservices(id_barber, datetime_booking):

    params = {
        'staff_id': id_barber,
        'datetime': datetime_booking
    }

    response = requests.get("https://b70280.alteg.io/api/v1/book_services/86104", params=params, headers=headers)

    result = response.json()

    return result.get('services')

def post_create_record(post_variable):
    response = requests.post("https://b70280.alteg.io/api/v1/book_record/86104", headers=headers, json=post_variable)

    # result = response.json()

    return True if response.status_code == 201 else False

def main():
    get_barbers()
    # check_proxy()

if __name__ == '__main__':
    main()







#Параметр в возвращенных данных bookable - показывает статус
