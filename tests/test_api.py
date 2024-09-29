class TestReservePost:
    def test_ok_post(self, client):
        body = {"reservation_id": "98765",
                "product_id": "12",
                "quantity": 10,
                "timestamp": "2024-09-04T12:00:00Z"
                }
        response = client.post("/api/v1/reserve", json=body)
        print(response.json())
        assert response.status_code == 200
        assert response.json()['status'] == 'success'
        assert response.json()['reservation_id'] == '98765'
#
#     def test_many_goods(self, client):
#         body = {"reservation_id": "98765",
#                 "product_id": "12",
#                 "quantity": 10000,
#                 "timestamp": "2024-09-04T12:00:00Z"
#                 }
#         response = client.post("/reserve/", data=body)
#         print(response)
#         assert response.status_code == 200
#         assert response.json()['status'] == 'error'
#         assert response.json()['reservation_id'] == '98765'
#
#     def test_bad_goods(self, client):
#         body = {"reservation_id": "98765",
#                 "product_id": "11111111111",
#                 "quantity": 10000,
#                 "timestamp": "2024-09-04T12:00:00Z"
#                 }
#         response = client.post("/reserve/", data=body)
#         print(response)
#         assert response.status_code == 200
#         assert response.json()['status'] == 'error'
#         assert response.json()['reservation_id'] == '98765'
#
#     def test_bad_request(self, client):
#         body = {"reservation_id": "98765",
#                 "product_id": "12",
#                 "quantity": 'sd',
#                 "timestamp": "2024-09-04T12:00:00Z"
#                 }
#         response = client.post("/reserve/", data=body)
#         print(response)
#         assert response.status_code > 400
#
#     def test_bad_metod(self, client):
#         body = {'x': ''}
#         response = client.put("/reserve/")
#         print(response)
#         assert response.status_code > 400
#
#
# class TestReserveGet:
#     def test_ok_get(self, client):
#         response = client.get("/reserve/1")
#         print(response)
#         assert response.status_code == 200
#
#     def test_wrong_reserve(self, client):
#         response = client.get("/reserve/x")
#         print(response)
#         assert response.status_code == 404
