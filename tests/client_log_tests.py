"""Tests für Client-Logging Endpoint."""
from .base import TestCategory, http_request


class ClientLogTests(TestCategory):
    name = 'Client-Logging'
    description = 'Browser-Logs via /api/log/'

    @staticmethod
    def test_client_log_accepts_post():
        """POST /api/log/ mit page+action+detail → HTTP 200"""
        code, _ = http_request('/api/log/', method='POST',
                               data={'page': 'bvh_studio', 'action': 'test_runner',
                                     'detail': 'automated test'})
        if code != 200:
            return False, f'HTTP {code}'
        return True, 'OK'
