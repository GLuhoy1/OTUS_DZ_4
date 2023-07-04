import requests

BASE_URL = "https://ya.ru"
BASE_STATUS_CODE = 200

'''Приношу извинения за обращение в форме коментария внутри кода, но:
по какой-то причине не смог заставить pytest подхватывать переменную из одного файла с тесстом.
Не могли бы вы пояснить можно ли реализовать addoption внутри файла с тестами, или необходимо создавать 
фаил conftest?'''


def test_status_code(request_generation):
    url = request_generation["url"]
    status_code = request_generation["status_code"]
    response = requests.get(url)
    assert response.status_code == status_code
