def test_config_save_requires_authentication(client):
    response = client.post("/api/config/save", json={"rms_min": 2.0})
    assert response.status_code == 401


def test_config_reset_requires_authentication(client):
    response = client.post("/api/config/reset")
    assert response.status_code == 401


def test_config_current_remains_public_for_device_reads(client):
    response = client.get("/api/config/current")
    assert response.status_code == 200
    assert "params" in response.json()
