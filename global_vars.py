# Variables globales
_global_state = {
    "current_user": None,
    "app_settings": {},
    "is_active": False,
    "last_message": "",
    "session_data": {},
    "wifi_status": False  # Nueva variable para el estado del WiFi
}

def get_global_var(key):
    """Obtener el valor de una variable global"""
    return _global_state.get(key)

def set_global_var(key, value):
    """Establecer el valor de una variable global"""
    _global_state[key] = value
    return True

def update_global_state(new_state):
    """Actualizar múltiples variables globales a la vez"""
    _global_state.update(new_state)
