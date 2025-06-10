import sys
from typing import Optional

from .account import get_local_account_info, clean_local_account_info, save_local_account_info, do_login
from .config import BuckyOSConfig, set_current_config, get_bucky_os_config, get_app_id, get_zone_host_name, AccountInfo, \
    set_account_info


async def init_bucky_os(config: BuckyOSConfig) -> None:
    if get_bucky_os_config():
        print("BuckyOS WebSDK is already initialized!")
        return

    if config:
        set_current_config(config)
    else:
        print("missing BuckyOSConfig")
        return

def get_runtime_type() -> str:
    return f"Python-{sys.version}"

def get_account_info() -> Optional[AccountInfo]:
    if get_account_info():
        return get_account_info()

    if not get_bucky_os_config():
        print("BuckyOS WebSDK is not initialized, call init_bucky_os first")
        return None

    return None

async def login(username: str, password: str, auto_login: bool = True) -> Optional[AccountInfo]:
    if not get_bucky_os_config():
        print("BuckyOS WebSDK is not initialized, call init_bucky_os first")
        return None

    app_id = get_app_id()
    if not app_id:
        print("BuckyOS WebSDK is not initialized, call init_bucky_os first")
        return None

    if auto_login:
        account_info = get_local_account_info(app_id)
        if account_info:
            set_account_info(account_info)
            return account_info

    clean_local_account_info(app_id)
    zone_host_name = get_zone_host_name()
    if not zone_host_name:
        print("BuckyOS WebSDK is not initialized, call init_bucky_os first")
        return None

    try:
        account_info = await do_login(username, password)
        if account_info:
            save_local_account_info(app_id, account_info)
            set_account_info(account_info)
        return account_info
    except Exception as e:
        print(f"login failed: {e}")
        raise

def logout(clean_account_info: bool = True) -> None:
    if not get_bucky_os_config():
        print("BuckyOS WebSDK is not initialized, call init_bucky_os first")
        return

    app_id = get_app_id()
    if not app_id:
        print("BuckyOS WebSDK is not initialized, call init_bucky_os first")
        return

    if not get_account_info():
        print("BuckyOS WebSDK is not login, call login first")
        return

    if clean_account_info:
        clean_local_account_info(app_id)


