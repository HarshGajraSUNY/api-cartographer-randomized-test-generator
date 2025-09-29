# conftest.py
import pytest
import uvicorn
import threading
import time
from mock_api import app


class Server(uvicorn.Server):
    def __init__(self, config: uvicorn.Config):
        super().__init__(config)
        self.thread = None

    def install_signal_handlers(self):
        pass

    def run_in_thread(self):
        self.thread = threading.Thread(target=self.run)
        self.thread.start()
        while not self.started:
            time.sleep(1e-3)

    def stop(self):
        self.should_exit = True
        self.thread.join()


@pytest.fixture(scope="session")
def api_server():
    """Starts the mock API server in a background thread for the test session."""
    config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="info")
    server = Server(config=config)

    server.run_in_thread()
    yield
    server.stop()
