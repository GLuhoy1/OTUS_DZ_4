import json
import pytest
import requests
from faker import Faker
import cerberus

fake = Faker()


# тест на проверку создания поста
def test_create_fake_post():
    url = 'https://jsonplaceholder.typicode.com/posts'
    data = {
        'title': fake.sentence(),
        'body': fake.paragraph(),
    }

    headers = {
        'Content-type': 'application/json; charset=UTF-8'
    }
    response = requests.post(url, data=json.dumps(data), headers=headers)
    json_response = response.json()
    assert response.status_code == 201
    assert data['title'] == json_response['title'] and data['body'] == json_response['body']


def test_form_of_all_posts():
    schema = {
        "userId": {"type": "integer"},
        "id": {"type": "integer"},
        "title": {"type": "string"},
        "body": {"type": "string"}
    }
    v = cerberus.Validator()
    response = requests.get("https://jsonplaceholder.typicode.com/posts")
    assert response.status_code == 200
    posts = response.json()
    for post in posts:
        assert v.validate(post, schema)


# проверка функции редактирования поста
@pytest.mark.parametrize('data, field_name', [
    ({'title': 'foo'}, 'title'),
    ({'title': 'bar'}, 'title'),
    ({'title': 'baz'}, 'title'),
    ({'body': 'Lorem ipsum dolor sit amet'}, 'body'),
    ({'body': 'Lorem ipsum'}, 'body'),
    ({'body': 'Hello, World!'}, 'body')
])
def test_of_patch_function(data, field_name):
    url = 'https://jsonplaceholder.typicode.com/posts/1'
    headers = {'Content-type': 'application/json; charset=UTF-8'}
    response = requests.patch(url, headers=headers, data=json.dumps(data))
    assert response.status_code == 200
    assert response.json()[field_name] == data[field_name]


@pytest.mark.parametrize('params', [
    {'userId': 1},
    {'userId': 2},
    {'userId': 3}
])
def test_of_sorting(params):
    response = requests.get('https://jsonplaceholder.typicode.com/posts', params=params)
    assert response.status_code == 200
    json_data = response.json()
    for item in json_data:
        assert item['userId'] == params['userId']


@pytest.mark.parametrize('num', (1, 2, 3))
def test_of_deleting(num):
    response = requests.delete(f'https://jsonplaceholder.typicode.com/posts/{num}')
    assert response.status_code == 200
