import pytest
import requests
import redis


r = redis.Redis(host='localhost', port=6379, db=0)
r.flushall()


def test_post_flushing_db():
    r.set('RTY', '45')
    response = requests.post('http://localhost:5000/database?merge=0', json={"cur": "BUL", "value": "17"})
    assert r.get('RTY') is None
    assert response.status_code == 200


def test_post_with_one_currency():
    response = requests.post('http://localhost:5000/database?merge=1', json={"cur": "BUL", "value": "17"})
    assert r.get('BUL') == b'17'
    assert response.status_code == 200


def test_post_with_list_of_currencies():
    response = requests.post('http://localhost:5000/database?merge=1',
                             json={"cur": ["EWQ", "GHT", "ERV"], "value": ["25", "45", "19"]})
    assert r.get('EWQ') == b'25' and r.get('GHT') == b'45' and r.get('ERV') == b'19'
    assert response.status_code == 200

#############


def test_post_with_list_length_mismatch():
    response = requests.post('http://localhost:5000/database?merge=1',
                             json={"cur": ["FTR", "EWP"], "value": ["25", "45", "19"]})
    assert response.status_code == 500


def test_post_with_different_elements_type():
    response = requests.post('http://localhost:5000/database?merge=1', json={"cur": ["FTR"], "value": "25"})
    print(response.json())
    assert response.status_code == 500


def test_post_with_letters_in_value():
    response = requests.post('http://localhost:5000/database?merge=1', json={"cur": "RTY", "value": "FR"})
    assert response.status_code == 500


def test_post_with_digit_in_currency():
    response = requests.post('http://localhost:5000/database?merge=1', json={"cur": ["45", "RTF"], "value": "45"})
    assert response.status_code == 500


def test_post_with_invalid_merge():
    response = requests.post('http://localhost:5000/database?merge=6', json={"cur": "BUL", "value": "17"})
    assert response.status_code == 500


def test_post_no_data():
    response = requests.post('http://localhost:5000/database?merge=0', json={})
    assert response.status_code == 500


