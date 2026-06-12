import sys
import os
import pytest
from unittest.mock import patch, MagicMock

def test_main_bootstrap_success(capsys) -> None:
    with patch("sys.argv", ["bibliomodel", "help"]):
        with patch("src.main.INIConfigAdapter") as mock_config_class, \
             patch("src.main.JSONPersistenceAdapter") as mock_repo_class, \
             patch("src.main.CLIController") as mock_controller_class:
            
            mock_controller = MagicMock()
            mock_controller.execute.return_value = "Mocked help output"
            mock_controller_class.return_value = mock_controller
            
            from src.main import main
            main()
            
            captured = capsys.readouterr()
            assert "Mocked help output" in captured.out

def test_main_permission_error_handling(capsys) -> None:
    with patch("sys.argv", ["bibliomodel", "help"]):
        with patch("src.main.INIConfigAdapter", side_effect=PermissionError("Access Denied")):
            from src.main import main
            with pytest.raises(SystemExit) as excinfo:
                main()
            assert excinfo.value.code == 1
            captured = capsys.readouterr()
            assert "[ERROR]" in captured.out
            assert "Permission failure" in captured.out
