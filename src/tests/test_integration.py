import pytest
from src.main import main
from unittest.mock import patch
from io import StringIO

class TestMainIntegration:
    @patch('sys.stdout', new_callable=StringIO)
    def test_clipboard_mode(self, mock_stdout):
        with patch('sys.argv', ['script.py', '--mode', 'clipboard']):
            main()
            output = mock_stdout.getvalue()
            assert "Job data extracted" in output