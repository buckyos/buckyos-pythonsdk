import sys
from typing import Optional, Dict, Any

from account import get_local_account_info, clean_local_account_info, save_local_account_info, do_login
from krpc_client import kRPCClient

BS_SERVICE_VERIFY_HUB = "verify_hub"

class AccountInfo:
    def __init__(self, data: Dict[str, Any]):
        self.data = data

class BuckyOSConfig:
    def __init__(self, zone_host_name: str, appid: str, default_protocol: str = "http://"):
        self.zone_host_name = zone_host_name
        self.appid = appid
        self.default_protocol = default_protocol

_current_config: Optional[BuckyOSConfig] = None
_current_account_info: Optional[AccountInfo] = None

async def init_bucky_os(config: BuckyOSConfig) -> None:
    global _current_config
    if _current_config:
        print("BuckyOS WebSDK is already initialized!")
        return

    if config:
        _current_config = config
    else:
        print("missing BuckyOSConfig")
        return

def get_runtime_type() -> str:
    return f"Python-{sys.version}"

def get_account_info() -> Optional[AccountInfo]:
    if _current_account_info:
        return _current_account_info

    if not _current_config:
        print("BuckyOS WebSDK is not initialized, call init_bucky_os first")
        return None

    return None

async def login(username: str, password: str, auto_login: bool = True) -> Optional[AccountInfo]:
    global _current_account_info
    if not _current_config:
        print("BuckyOS WebSDK is not initialized, call init_bucky_os first")
        return None

    app_id = get_app_id()
    if not app_id:
        print("BuckyOS WebSDK is not initialized, call init_bucky_os first")
        return None

    if auto_login:
        account_info = get_local_account_info(app_id)
        if account_info:
            _current_account_info = account_info
            return _current_account_info

    clean_local_account_info(app_id)
    zone_host_name = get_zone_host_name()
    if not zone_host_name:
        print("BuckyOS WebSDK is not initialized, call init_bucky_os first")
        return None

    try:
        account_info = do_login(username, password)
        if account_info:
            save_local_account_info(app_id, account_info)
            _current_account_info = account_info
        return account_info
    except Exception as e:
        print(f"login failed: {e}")
        raise

def logout(clean_account_info: bool = True) -> None:
    if not _current_config:
        print("BuckyOS WebSDK is not initialized, call init_bucky_os first")
        return

    app_id = get_app_id()
    if not app_id:
        print("BuckyOS WebSDK is not initialized, call init_bucky_os first")
        return

    if not _current_account_info:
        print("BuckyOS WebSDK is not login, call login first")
        return

    if clean_account_info:
        clean_local_account_info(app_id)


def get_zone_host_name() -> Optional[str]:
    if not _current_config:
        print("BuckyOS WebSDK is not initialized, call init_bucky_os first")
        return None
    return _current_config.zone_host_name


def get_zone_service_url(service_name: str) -> str:
    if not _current_config:
        raise Exception("BuckyOS WebSDK is not initialized, call init_bucky_os first")
    return f"{_current_config.default_protocol}{_current_config.zone_host_name}/kapi/{service_name}"


def get_service_rpc_client(service_name: str) -> kRPCClient:
    if not _current_config:
        print("BuckyOS WebSDK is not initialized, call init_bucky_os first")
        raise Exception("BuckyOS WebSDK is not initialized, call init_bucky_os first")

    session_token = None
    if _current_account_info and hasattr(_current_account_info, 'session_token'):
        session_token = _current_account_info.session_token

    return kRPCClient(get_zone_service_url(service_name), session_token)


def get_app_id() -> Optional[str]:
    if _current_config:
        return _current_config.appid
    print("BuckyOS WebSDK is not initialized, call init_bucky_os first")
    return None


def get_bucky_os_config() -> Optional[BuckyOSConfig]:
    return _current_config
