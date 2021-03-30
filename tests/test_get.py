import pytest
import requests
import redis
from scripts.redis_client import *

def set_up():
    #r = redis.Redis(host='0.0.0.0', port=6379, db=0)
    #r = redis.Redis(host='redis', port=6379, db=0)
    r.flushall()
    r.set('USD', '87')
    r.set('EUR', '96')
    r.set('TRE', '23')
    r.set('YRE', '54')
    r.set('WER', '12')

class TestGetSuccess:
    def test_conversion(self):
        set_up()
        response = requests.get('http://localhost:5000/conversion?from=USD&to=TRE&amount=123')
        assert response.json()["result"] == '465.26'
        assert response.status_code == 200

    def test_get_from_rur(self):
        response = requests.get('http://localhost:5000/conversion?from=RUR&to=WER&amount=110')
        assert response.json()["result"] == '9.17'
        assert response.status_code == 200

    def test_get_to_rur(self):
        response = requests.get('http://localhost:5000/conversion?from=YRE&to=RUR&amount=110')
        assert response.json()["result"] == '5940.0'
        assert response.status_code == 200


class TestGetError:
    def test_get_from_rur_to_rur(self):
        response = requests.get('http://localhost:5000/conversion?from=RUR&to=RUR&amount=12')
        assert response.status_code == 422

    def test_get_from_digit(self):
        response = requests.get('http://localhost:5000/conversion?from=45&to=RUR&amount=12')
        assert response.status_code == 415

    def test_get_to_digit(self):
        response = requests.get('http://localhost:5000/conversion?from=RUR&to=23&amount=12')
        assert response.status_code == 415

    def test_uri_mistake(self):
        response = requests.get('http://localhost:5000/conversion?from=RUR&to=USD&amnt=12')
        assert response.status_code == 400

