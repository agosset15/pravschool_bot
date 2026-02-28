import hashlib

from . import json


def get_webhook_hash(webhook_data: dict) -> str:
    return hashlib.sha256(json.bytes_encode(webhook_data)).hexdigest()


def encode_ns_password(password: str) -> bytes:
    return hashlib.md5(password.encode("windows-1251")).hexdigest().encode()


def get_ns_request_hash(request_data: tuple) -> str:
    if request_data == ():
        return ""
    return hashlib.sha256(json.bytes_encode(request_data)).hexdigest()
