import pytest
import requests
import redis


r = redis.Redis(host='0.0.0.0', port=6379, db=0)
#r = redis.Redis(host='redis', port=6379, db=0)
r.flushall()


class TestPostSuccess:
    def test_post_flushing_db(self):
        r.set('RTY', '45')
        response = requests.post('http://localhost:5000/database?merge=0', json={"cur": "BUL", "value": "17"})
        assert r.get('RTY') is None
        assert response.status_code == 201

    def test_post_with_one_currency(self):
        response = requests.post('http://localhost:5000/database?merge=1', json={"cur": "BUL", "value": "17"})
        assert r.get('BUL') == b'17'
        assert response.status_code == 201

    def test_post_with_list_of_currencies(self):
        response = requests.post('http://localhost:5000/database?merge=1',
                                 json={"cur": ["EWQ", "GHT", "ERV"], "value": ["25", "45", "19"]})
        assert r.get('EWQ') == b'25' and r.get('GHT') == b'45' and r.get('ERV') == b'19'
        assert response.status_code == 201


class TestPostError:
    def test_post_with_list_length_mismatch(self):
        response = requests.post('http://localhost:5000/database?merge=1',
                                 json={"cur": ["FTR", "EWP"], "value": ["25", "45", "19"]})
        assert response.status_code == 422

    def test_post_with_different_elements_type(self):
        response = requests.post('http://localhost:5000/database?merge=1', json={"cur": ["FTR"], "value": "25"})
        print(response.json())
        assert response.status_code == 422

    def test_post_with_letters_in_value(self):
        response = requests.post('http://localhost:5000/database?merge=1', json={"cur": "RTY", "value": "FR"})
        assert response.status_code == 415

    def test_post_with_digit_in_currency(self):
        response = requests.post('http://localhost:5000/database?merge=1', json={"cur": ["45", "RTF"], "value": ["45", "34"]})
        assert response.status_code == 415

    def test_post_with_invalid_merge(self):
        response = requests.post('http://localhost:5000/database?merge=6', json={"cur": "BUL", "value": "17"})
        assert response.status_code == 422

    def test_post_no_data(self):
        response = requests.post('http://localhost:5000/database?merge=0')
        assert response.status_code == 422


