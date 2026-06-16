from app.services import hello_world as hello_world_service


def test_get_count_returns_zero_initially():
    # Arrange — counter reset by fixture

    # Act
    count = hello_world_service.get_count()

    # Assert
    assert count == 0


def test_increment_returns_one_on_first_click():
    # Arrange — counter at 0

    # Act
    count = hello_world_service.increment()

    # Assert
    assert count == 1


def test_increment_accumulates():
    # Arrange
    hello_world_service.increment()

    # Act
    count = hello_world_service.increment()

    # Assert
    assert count == 2


def test_reset_count_clears_counter():
    # Arrange
    hello_world_service.increment()
    hello_world_service.increment()

    # Act
    hello_world_service.reset_count()

    # Assert
    assert hello_world_service.get_count() == 0


def test_get_hello_world_count_route_returns_zero(client):
    # Arrange — fresh counter

    # Act
    response = client.get("/hello-world/count")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"count": 0}


def test_increment_hello_world_count_route_increments(client):
    # Arrange — fresh counter

    # Act
    response = client.post("/hello-world/click")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"count": 1}


def test_sequential_clicks_increment_count(client):
    # Arrange
    client.post("/hello-world/click")

    # Act
    second = client.post("/hello-world/click")
    third = client.post("/hello-world/click")

    # Assert
    assert second.json() == {"count": 2}
    assert third.json() == {"count": 3}


def test_get_reflects_total_after_clicks(client):
    # Arrange
    client.post("/hello-world/click")
    client.post("/hello-world/click")

    # Act
    response = client.get("/hello-world/count")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"count": 2}
