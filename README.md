# currency conversion
Python REST API for currency conversion based on aiohttp

Requires aiohttp 3.7.4, redis 3.5.3, python 3.8

Dockerized:
docker-compose up -d 


Works on socket
http://localhost:5000/

Handle 2 operations:

GET http://localhost:5000/conversion?from=BUL&to=RTY&amount=10

POST http://localhost:5000/database?merge=1 to merge data 
or merge = 0 to delete old data 
+ json.
Json data example:
{
  "cur": ["EUR", "USD", "KJH", "YUT"], 
  "value": ["85", "74", "32", "14"]
}
or single:
{
  "cur": "UYT", 
  "value": "74"
}
cur is currency
value - currency price in rubles.

Testing runs:
pytest tests
