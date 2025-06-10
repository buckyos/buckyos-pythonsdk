import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional
from localStoragePy import localStoragePy
from .config import get_app_id
from .krpc_client import get_service_rpc_client

BS_SERVICE_VERIFY_HUB = "verify_hub"


localStorage = localStoragePy()


class AccountInfo:
    def __init__(self, user_name: str, user_id: str, user_type: str, session_token: str):
        self.user_name = user_name
        self.user_id = user_id
        self.user_type = user_type
        self.session_token = session_token

LOGIN_EVENT = 'onLogin'

def hash_password(username: str, password: str, nonce: Optional[int] = None) -> str:
    sha256 = hashlib.sha256()
    sha256.update(f"{password}{username}.buckyos".encode('utf-8'))
    org_password_hash_str = sha256.hexdigest()

    if nonce is None:
        return org_password_hash_str

    sha256 = hashlib.sha256()
    salt = f"{org_password_hash_str}{nonce}"
    sha256.update(salt.encode('utf-8'))
    return sha256.hexdigest()

def clean_local_account_info(app_id: str) -> None:
    if 'buckyos.account_info' in localStorage:
        del localStorage['buckyos.account_info']

    cookie_options = {
        'path': '/',
        'expires': datetime.utcnow() - timedelta(days=1),
        'secure': True,
        'samesite': 'Lax'
    }
    cookie_str = f"{app_id}_token=; " + "; ".join(f"{k}={v}" for k, v in cookie_options.items())
    localStorage.setItem("cookie", cookie_str)

def save_local_account_info(app_id: str, account_info: AccountInfo) -> None:
    if account_info.session_token is None:
        print("session_token is null, can't save account info")
        return

    localStorage['buckyos.account_info'] = json.dumps(account_info.__dict__)

    cookie_options = {
        'path': '/',
        'expires': datetime.utcnow() + timedelta(days=30),
        'secure': True,
        'samesite': 'Lax'
    }
    cookie_str = f"{app_id}_token={account_info.session_token}; " + "; ".join(f"{k}={v}" for k, v in cookie_options.items())
    localStorage.setItem("cookie", cookie_str)

def get_local_account_info(app_id: str) -> Optional[AccountInfo]:
    account_info_str = localStorage.get('buckyos.account_info')
    if account_info_str is None:
        return None

    account_dict = json.loads(account_info_str)
    return AccountInfo(**account_dict)

async def do_login(username: str, password: str) -> Optional[AccountInfo]:
    app_id = get_app_id()
    if app_id is None:
        print("BuckyOS WebSDK is not initialized, call init_buckyos first")
        return None

    login_nonce = int(datetime.now().timestamp() * 1000)
    password_hash = hash_password(username, password, login_nonce)
    print(f"password_hash: {password_hash}")

    if 'account_info' in localStorage:
        del localStorage['account_info']

    try:
        rpc_client = get_service_rpc_client(BS_SERVICE_VERIFY_HUB)
        rpc_client.set_seq(login_nonce)
        account_info = await rpc_client.call("login", {
            'type': 'password',
            'username': username,
            'password': password_hash,
            'appid': app_id,
        })

        save_local_account_info(app_id, AccountInfo(**account_info))
        return account_info
    except Exception as error:
        print(f"login failed: {error}")
        raise error


