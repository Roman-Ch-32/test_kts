import json


class TestReservePost:

    def test_create_test_products(self, client):
        with open('app/mock_product.json') as f:
            data = json.load(f)
        body = {'products': data}
        response = client.post("/api/v1/product", json=body)
        assert response.status_code == 200
        assert response.json()['status'] == 'success'

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

    def test_many_goods(self, client):
        body = {"reservation_id": "98765",
                "product_id": "14",
                "quantity": 10000,
                "timestamp": "2024-09-04T12:00:00Z"
                }
        response = client.post("/api/v1/reserve/", json=body)
        print(response)
        assert response.status_code == 200
        assert response.json()['status'] == 'error'
        assert response.json()['reservation_id'] == '98765'

    def test_bad_goods(self, client):
        body = {"reservation_id": "98765",
                "product_id": "111111111",
                "quantity": 10,
                "timestamp": "2024-09-04T12:00:00Z"
                }
        response = client.post("/api/v1/reserve/", json=body)
        print(response)
        assert response.status_code == 200
        assert response.json()['status'] == 'error'
        assert response.json()['reservation_id'] == '98765'

    def test_bad_request(self, client):
        body = {"reservation_id": "98765",
                "product_id": "12",
                "quantity": 'sd',
                "timestamp": "2024-09-04T12:00:00Z"
                }
        response = client.post("/api/v1/reserve/", json=body)
        print(response)
        assert response.status_code == 422

    def test_bad_metod(self, client):
        body = {'x': ''}
        response = client.put("/api/v1/reserve/")
        print(response)
        assert response.status_code == 405


class TestReserveGet:
    def test_ok_get(self, client):
        response = client.get("/api/v1/reserve/98765")
        print(response.json())
        assert response.status_code == 200

    def test_wrong_reserve(self, client):
        response = client.get("/api/v1/reserve/x")
        print(response.json())
        assert response.status_code == 404
