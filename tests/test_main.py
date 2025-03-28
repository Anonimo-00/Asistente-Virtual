import pytest
from main import print_global_vars
import logging

class TestPrintGlobalVars:
    """Pruebas para la función print_global_vars"""

    def test_logs_all_global_variables(self, mocker):
        """Verifica que se registren todas las variables globales"""
        mock_logger = mocker.patch('main.logger')
        mock_time = mocker.patch('time.sleep', side_effect=InterruptedError)
        mock_global_state = {
            "current_user": "test_user",
            "app_settings": {"theme": "dark"},
            "is_active": True,
            "last_message": "Hello",
            "session_data": {"token": "abc123"},
            "wifi_status": True
        }
        
        mocker.patch('main._global_state', mock_global_state)
        
        with pytest.raises(InterruptedError):
            print_global_vars()
        
        mock_logger.info.assert_any_call("\n=== Estado de Variables Globales ===")
        
        for key, value in mock_global_state.items():
            mock_logger.info.assert_any_call(f"{key}: {value}")
        
        mock_logger.info.assert_any_call("=" * 35)

    def test_handles_empty_global_state(self, mocker):
        """Verifica el manejo de un diccionario global_state vacío"""
        mock_logger = mocker.patch('main.logger')
        mock_time = mocker.patch('time.sleep', side_effect=InterruptedError)
        
        mocker.patch('main._global_state', {})
        
        with pytest.raises(InterruptedError):
            print_global_vars()
        
        mock_logger.info.assert_any_call("\n=== Estado de Variables Globales ===")
        assert mock_logger.info.call_count == 2
        mock_logger.info.assert_any_call("=" * 35)

if __name__ == '__main__':
    pytest.main([__file__])
