from django.apps import AppConfig


class TestappConfig(AppConfig):
    name = "testapp"

    # import signal handlers
    import tests.testapp.handlers
