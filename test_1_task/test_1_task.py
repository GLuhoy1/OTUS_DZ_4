import cerberus
import requests
import pytest
import random

BASE_URL = "https://dog.ceo/api/"


# проверка формы JSON файла при запросе нескольких случайных изображений
@pytest.mark.parametrize("count", [1, 2, 5, 30])
def test_random_images_structure(count):
    scheme_for_random_images = {
        "message": {"type": "list", "schema": {"type": "string"}},
        "status": {"type": "string", "allowed": ["success"]}
    }
    response = requests.get(f'{BASE_URL}breeds/image/random/{str(count)}')
    v = cerberus.Validator()
    assert response.status_code == 200
    assert v.validate(response.json(), scheme_for_random_images)


# проверка на факт выдачи сайтом при двух последовательных запросах несовпадающих изображений
@pytest.mark.parametrize("iteration", range(10))
def test_really_random_image(iteration):
    first_response = requests.get(f'{BASE_URL}breeds/image/random')
    second_response = requests.get(f'{BASE_URL}breeds/image/random')
    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert first_response.json()["message"] != second_response.json()["message"]


# проверка соответствия формы списка всех пород
def test_breed_list_api_response():
    scheme_for_all_breeds = {
        "message": {
            "type": "dict",
            "valuesrules": {
                "type": "list",
                "schema": {"type": "string"}
            }
        },
        "status": {"type": "string"}
    }
    response = requests.get(f'{BASE_URL}breeds/list/all')
    v = cerberus.Validator()
    assert response.status_code == 200
    assert v.validate(response.json(), scheme_for_all_breeds)


# фикстура создаёт словарь с породами у которых есть подпороды
@pytest.fixture
def breeds_with_subbreeds():
    response = requests.get(f"{BASE_URL}breeds/list/all")
    data = response.json()
    breeds_with_subbreeds = []
    for breed, subbreeds in data["message"].items():
        if subbreeds:
            breed_with_subbreeds = {
                "breed": breed,
                "subbreeds": subbreeds
            }
            breeds_with_subbreeds.append(breed_with_subbreeds)
    return breeds_with_subbreeds


# фикстура возвращает 5 случайных пород с подпородами
@pytest.fixture(params=[i for i in range(5)])
def random_breed_with_subbreed(breeds_with_subbreeds):
    breed_with_subbreeds = random.choice(breeds_with_subbreeds)
    return breed_with_subbreeds


# тест проверят соответствие списка подпород полученых разными способами
def test_compare_subbreeds(random_breed_with_subbreed, breeds_with_subbreeds):
    breed_name = random_breed_with_subbreed["breed"]
    expected_subbreeds = random_breed_with_subbreed["subbreeds"]
    url = f"{BASE_URL}breed/{breed_name}/list"
    response = requests.get(url)
    assert response.status_code == 200
    assert breed_name in [breed["breed"] for breed in breeds_with_subbreeds]
    assert set(expected_subbreeds) == set(response.json()["message"])


# фикстура создаёт список всех пород
@pytest.fixture
def all_breeds():
    response = requests.get(f"{BASE_URL}breeds/list/all")
    data = response.json()
    breeds = list(data["message"].keys())
    return breeds


# проверяет существование ссылки на картинку при запросе рандобного изображения
@pytest.mark.parametrize("test_num", range(5))
def test_check_breed_image_existence(test_num, all_breeds):
    breed = random.choice(all_breeds)
    url = f"{BASE_URL}breed/{breed}/images/random"
    response = requests.get(url)
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] is not None


"""Приношу извенения за излишнее использование фикстур, я понимаю что они здесь
не оправданны поскольку используются по сути один раз"""
