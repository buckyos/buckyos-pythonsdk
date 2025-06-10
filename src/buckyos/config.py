from typing import Optional, Dict, Any


class BuckyOSConfig:
    def __init__(self, zone_host_name: str, appid: str, default_protocol: str = "http://"):
        self.zone_host_name = zone_host_name
        self.appid = appid
        self.default_protocol = default_protocol


_current_config: Optional[BuckyOSConfig] = None

def get_bucky_os_config() -> Optional[BuckyOSConfig]:
    return _current_config

def set_current_config(config: BuckyOSConfig) -> None:
    global _current_config
    _current_config = config

def get_zone_host_name() -> Optional[str]:
    if not _current_config:
        print("BuckyOS WebSDK is not initialized, call init_bucky_os first")
        return None
    return _current_config.zone_host_name


def get_app_id() -> Optional[str]:
    if _current_config:
        return _current_config.appid
    print("BuckyOS WebSDK is not initialized, call init_bucky_os first")
    return None



class AccountInfo:
    def __init__(self, data: Dict[str, Any]):
        self.data = data


_current_account_info: Optional[AccountInfo] = None

def get_account_info() -> Optional[AccountInfo]:
    return _current_account_info

def set_account_info(account_info: AccountInfo) -> None:
    global _current_account_info
    _current_account_info = account_info
