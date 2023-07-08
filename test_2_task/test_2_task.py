import cerberus
import requests
import pytest
import random
from faker import Faker
from geopy.distance import geodesic

BASE_URL = "https://api.openbrewerydb.org/"

TYPE_OF_BREWERIES = ('micro', 'nano', 'regional', 'brewpub', 'large', 'planning', 'bar',
                     'contract', 'proprietor', 'closed')


# Проверка соответсвтия списка всех пивоварен
@pytest.mark.parametrize("number_of_brewiers_per_page", [random.randint(1, 50) for _ in range(10)])
def test_brewery_list_shema(number_of_brewiers_per_page):
    schema_for_brewery = {
        "id": {'type': 'string'},
        "name": {'type': 'string'},
        "brewery_type": {'type': 'string'},
        "address_1": {'type': 'string', 'nullable': True},
        "address_2": {'type': 'string', 'nullable': True},
        "address_3": {'type': 'string', 'nullable': True},
        "city": {'type': 'string'},
        "state_province": {'type': 'string'},
        "postal_code": {'type': 'string'},
        "country": {'type': 'string'},
        "longitude": {'type': 'string', 'nullable': True},
        "latitude": {'type': 'string', 'nullable': True},
        "phone": {'type': 'string', 'nullable': True},
        "website_url": {'type': 'string', 'nullable': True},
        "state": {'type': 'string', 'nullable': True},
        "street": {'type': 'string', 'nullable': True}
    }
    response = requests.get(f'{BASE_URL}v1/breweries?per_page={number_of_brewiers_per_page}')
    v = cerberus.Validator()
    assert response.status_code == 200
    breweries = response.json()
    for brewery in breweries:
        assert v.validate(brewery, schema_for_brewery)


# проверка коректности сортировки по размеру пивоварен
# P.S. с малой переодичностю приходит ответ от сервера с кодом 502, в случае большого количества повторностей
@pytest.mark.parametrize("type_of_breweries", TYPE_OF_BREWERIES * 5)
def test_sorting_correctness(type_of_breweries):
    response = requests.get(f'{BASE_URL}v1/breweries?by_type={type_of_breweries}&per_page=50')
    assert response.status_code == 200
    breweries = response.json()
    for brewery in breweries:
        assert brewery["brewery_type"] == type_of_breweries


# тест на создание фэйковой пивоварни
def test_create_brewery_negative():
    fake = Faker()
    invalid_data = {
        "name": fake.name(),
        "brewery_type": fake.word(),
        "city": fake.city(),
        "state_province": fake.state(),
        "postal_code": fake.zipcode(),
        "country": fake.country()
    }
    response = requests.post("https://api.openbrewerydb.org/breweries", json=invalid_data)
    assert response.status_code == 404


# проверка правильности сортировки пивоварен по удалённости от точки
@pytest.mark.parametrize("lat, lon, per_page, place_name", [
    (55.751244, 37.618423, 5, "Moscow"),
    (41.0082, 28.9784, 10, "Istanbul")
], ids=["moscow", "istanbul"])
def test_brewery_distance_sort(lat, lon, per_page, place_name):
    url = f"https://api.openbrewerydb.org/v1/breweries?by_dist={lat},{lon}&per_page={per_page}"
    response = requests.get(url)
    assert response.status_code == 200
    breweries = response.json()
    assert len(breweries) > 0
    for i in range(len(breweries) - 1):
        brewery1 = breweries[i]
        brewery2 = breweries[i + 1]
        coords1 = (float(brewery1["latitude"]), float(brewery1["longitude"]))
        coords2 = (float(brewery2["latitude"]), float(brewery2["longitude"]))
        distance1 = geodesic((lat, lon), coords1).km
        distance2 = geodesic((lat, lon), coords2).km
        assert distance1 <= distance2


# проверка что при запросе 0 пивоварен на странице ответ с сайта пустой
def test_empty_json_response():
    url = "https://api.openbrewerydb.org/v1/breweries?per_page=0"
    response = requests.get(url)
    assert response.status_code == 200
    assert response.json() == []
