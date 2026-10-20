from app import create_app


def test_metrics_endpoint():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    client = app.test_client()

    # Generate a successful HTTP request
    response = client.get("/health")
    assert response.status_code == 200

    # Verify the Prometheus endpoint
    response = client.get("/metrics")
    assert response.status_code == 200

    metrics = response.get_data(as_text=True)

    assert "flask_http_request_total" in metrics
    assert "flask_http_request_duration_seconds_bucket" in metrics
    assert 'method="GET",status="200"' in metrics


def test_metrics_record_server_errors():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    # A test-only endpoint that returns HTTP 500
    @app.route("/test-server-error")
    def simulated_error():
        return "Simulated server error", 500

    client = app.test_client()

    response = client.get("/test-server-error")
    assert response.status_code == 500

    response = client.get("/metrics")
    assert response.status_code == 200

    metrics = response.get_data(as_text=True)

    # Verify the exporter recorded the 500 response
    assert 'flask_http_request_total{method="GET",status="500"}' in metrics
    assert "flask_http_request_duration_seconds" in metrics
