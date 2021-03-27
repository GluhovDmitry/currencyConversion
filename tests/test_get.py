import pytest
import requests
import redis


def setUp():
    r = redis.Redis(host='localhost', port=6379, db=0)
    r.flushall()
    r.set('USD', '87')
    r.set('EUR', '96')
    r.set('TRE', '23')
    r.set('YRE', '54')
    r.set('WER', '12')

def test_conversion():
    setUp()
    response = requests.get('http://localhost:5000/convert?from=USD&to=TRE&amount=123')
    assert response.json()["result"] == '465.26'
    assert response.status_code == 200


def test_get_from_rur():
    response = requests.get('http://localhost:5000/convert?from=RUR&to=WER&amount=110')
    assert response.json()["result"] == '9.17'
    assert response.status_code == 200


def test_get_to_rur():
    response = requests.get('http://localhost:5000/convert?from=YRE&to=RUR&amount=110')
    assert response.json()["result"] == '5940.0'
    assert response.status_code == 200

#######


def test_get_from_rur_to_rur():
    response = requests.get('http://localhost:5000/convert?from=RUR&to=RUR&amount=12')
    assert response.status_code == 500


def test_get_from_digit():
    response = requests.get('http://localhost:5000/convert?from=45&to=RUR&amount=12')
    assert response.status_code == 500


def test_get_to_digit():
    response = requests.get('http://localhost:5000/convert?from=RUR&to=23&amount=12')
    assert response.status_code == 500


def test_uri_mistake():
    response = requests.get('http://localhost:5000/convert?from=RUR&to=USD&amnt=12')
    assert response.status_code == 500

