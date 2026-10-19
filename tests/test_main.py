import contextlib
import io
import os
import unittest
from unittest.mock import patch

import redis

import main


class ClientTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {
            'REDIS_HOST': 'localhost', 'REDIS_PORT': '6379',
            'REDIS_DB': '0', 'REDIS_PASSWORD': 'test-secret',
            'REDIS_TIMEOUT': '0.5',
        }, clear=True)
        self.env.start()
        self.addCleanup(self.env.stop)
        loader = patch('main.load_dotenv')
        loader.start()
        self.addCleanup(loader.stop)

    def run_example(self):
        output, errors = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            status = main.main()
        self.assertNotIn('test-secret', errors.getvalue())
        return status, output.getvalue(), errors.getvalue()

    @patch('main.redis.Redis')
    def test_success_and_timeouts(self, factory):
        client = factory.return_value.__enter__.return_value
        client.get.return_value = b'Batata'
        status, output, errors = self.run_example()
        self.assertEqual(status, 0)
        self.assertEqual(output, 'Valor inserido: Batata\n')
        self.assertEqual(errors, '')
        self.assertEqual(factory.call_args.kwargs['socket_timeout'], 0.5)
        self.assertEqual(factory.call_args.kwargs['socket_connect_timeout'], 0.5)
        client.set.assert_called_once_with('Teste', 'Batata')
        factory.return_value.__exit__.assert_called_once()

    @patch('main.redis.Redis')
    def test_failures(self, factory):
        for exception, message in [
            (redis.exceptions.AuthenticationError, 'autenticação'),
            (redis.exceptions.ConnectionError, 'conectar'),
            (redis.exceptions.TimeoutError, 'Tempo limite'),
            (redis.exceptions.ResponseError, 'operação'),
        ]:
            with self.subTest(exception=exception):
                factory.return_value.__enter__.return_value.set.side_effect = exception('test-secret')
                status, output, errors = self.run_example()
                self.assertEqual(status, 1)
                self.assertEqual(output, '')
                self.assertIn(message, errors)

    @patch('main.redis.Redis')
    def test_invalid_configuration(self, factory):
        for key, value in [('REDIS_TIMEOUT', 'nan'), ('REDIS_TIMEOUT', '0'),
                           ('REDIS_PORT', 'invalid'), ('REDIS_DB', '-1'),
                           ('REDIS_PASSWORD', '')]:
            with self.subTest(key=key, value=value), patch.dict(os.environ, {key: value}):
                self.assertEqual(self.run_example()[0], 1)
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(self.run_example()[0], 1)
        factory.assert_not_called()


if __name__ == '__main__':
    unittest.main()
