1) Create Venv and then activate
2) python -m venv booking_venv

3) booking_venv\scripts\activate
4) Go to Project main repo and execute requirement file into venv
5) pip install -r requirements. txt
6) execute project using below command
7) python booking.py
8) Then test API using below Endpoints

9) For import file, hit below URL using POST method
10) Endpoint URL - http://127.0.0.1:5000/imoprt
11) For BOOKING API,  hit below URL using POST method
12) Endpoint URL - http://127.0.0.1:5000/book
13) Payload :-
14) {"member_id":30,
15) "inventory_id":1}
16) Bokking will be successfully if booking more than 2 then it will return Booking reached messgae
17) For Cancel Booking hit below API using POST method
18) Endpoint URL - http://127.0.0.1:5000/cancel/booking_id
19) All data will store in SQLite DB.

A
