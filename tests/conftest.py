import pytest
import os


def delete_files():
    for file in os.listdir("tests/coins_data"):
        os.remove(f"tests/coins_data/{file}")


@pytest.fixture(scope="session", autouse=True)
def clean_after_tests(request):
    request.addfinalizer(delete_files)
