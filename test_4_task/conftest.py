import pytest


def pytest_addoption(parser):
    parser.addoption("--url", action="store", type=str, default="https://ya.ru")
    parser.addoption("--status_code", action="store", type=int, default=200)


@pytest.fixture
def request_generation(request):
    url = request.config.getoption("--url")
    status_code = request.config.getoption("--status_code")
    return {"url": url, "status_code": status_code}
