import pytest


def pytest_collection_modifyitems(config, items):
    if config.getoption("base_url"):
        return

    skip_e2e = pytest.mark.skip(
        reason="E2E tests need --base-url pointing at a running TaskFlow app"
    )
    for item in items:
        if "e2e" in item.path.parts:
            item.add_marker(skip_e2e)