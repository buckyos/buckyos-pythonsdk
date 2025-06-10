import json
import time
from enum import Enum
from typing import Optional, Any
from .config import get_bucky_os_config, get_account_info
import requests


class RPCProtocolType(Enum):
    HttpPostJson = 'HttpPostJson'


class RPCError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.name = 'RPCError'


class kRPCClient:
    def __init__(self, url: str, token: Optional[str] = None, seq: Optional[int] = None):
        self.server_url = url
        self.protocol_type = RPCProtocolType.HttpPostJson
        # Use milliseconds timestamp as initial sequence number
        self.seq = seq if seq is not None else int(time.time() * 1000)
        self.session_token = token
        self.init_token = token

    async def call(self, method: str, params: Any) -> Any:
        return await self._call(method, params)

    def set_seq(self, seq: int) -> None:
        self.seq = seq

    async def _call(self, method: str, params: Any) -> Any:
        current_seq = self.seq
        self.seq += 1

        request_body = {
            "method": method,
            "params": params,
            "sys": [current_seq, self.session_token] if self.session_token else [current_seq]
        }

        try:
            response = requests.post(
                self.server_url,
                headers={'Content-Type': 'application/json'},
                data=json.dumps(request_body)
            )

            if not response.ok:
                raise RPCError(f"RPC call error: {response.status_code}")

            rpc_response = response.json()

            if "sys" in rpc_response:
                sys = rpc_response["sys"]
                if not isinstance(sys, list):
                    raise RPCError("sys is not array")

                if len(sys) > 1:
                    response_seq = sys[0]
                    if not isinstance(response_seq, int):
                        raise RPCError("sys[0] is not number")
                    if response_seq != current_seq:
                        raise RPCError(f"seq not match: {response_seq}!={current_seq}")

                if len(sys) > 2:
                    token = sys[1]
                    if not isinstance(token, str):
                        raise RPCError("sys[1] is not string")
                    self.session_token = token

            if "error" in rpc_response:
                raise RPCError(f"RPC call error: {rpc_response['error']}")

            return rpc_response.get("result")

        except requests.exceptions.RequestException as e:
            raise RPCError(f"RPC call failed: {str(e)}")
        except json.JSONDecodeError as e:
            raise RPCError(f"RPC response parsing failed: {str(e)}")
        except Exception as e:
            raise RPCError(f"Unexpected error: {str(e)}")


def get_zone_service_url(service_name: str) -> str:
    if not get_bucky_os_config():
        raise Exception("BuckyOS WebSDK is not initialized, call init_bucky_os first")
    return f"{get_bucky_os_config().default_protocol}{get_bucky_os_config().zone_host_name}/kapi/{service_name}"


def get_service_rpc_client(service_name: str) -> kRPCClient:
    if not get_bucky_os_config():
        print("BuckyOS WebSDK is not initialized, call init_bucky_os first")
        raise Exception("BuckyOS WebSDK is not initialized, call init_bucky_os first")

    session_token = None
    account_info = get_account_info()
    if account_info and hasattr(account_info, 'session_token'):
        session_token = account_info.session_token

    return kRPCClient(get_zone_service_url(service_name), session_token)
