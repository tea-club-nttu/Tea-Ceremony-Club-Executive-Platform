import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from utils.github_json_store import StorageError, save_json
from utils.calendar_store import save_events


class StorageErrorsTest(unittest.TestCase):
    def test_write_denied_is_reported(self):
        failure = HTTPError('https://api.github.com', 403, 'Forbidden', {}, None)
        with patch('utils.github_json_store.github_token', return_value='test'), patch(
            'utils.github_json_store.github_request', side_effect=[{'sha': 'abc'}, failure]
        ):
            with self.assertRaisesRegex(StorageError, 'HTTP 403'):
                save_json('data/calendar_events.json', [], 'test', strict=True)

    def test_failed_remote_save_does_not_write_local_file(self):
        with patch('utils.calendar_store.github_token', return_value='test'), patch(
            'utils.calendar_store.save_json', side_effect=StorageError('failed')
        ), patch('pathlib.Path.write_text') as write:
            with self.assertRaises(StorageError):
                save_events([])
            write.assert_not_called()

    def test_successful_remote_save(self):
        with patch('utils.github_json_store.github_token', return_value='test'), patch(
            'utils.github_json_store.github_request', side_effect=[{'sha': 'abc'}, {'commit': {}}]
        ):
            self.assertTrue(save_json('data/calendar_events.json', [], 'test', strict=True))
