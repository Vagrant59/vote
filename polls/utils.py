import hashlib
import random

ALL_CHARS = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'


def gen_md5_digest(content):
    """将字符串处理成MD5摘要"""
    return hashlib.md5(content.encode()).hexdigest()


def gen_random_code(length=4):
    return ''.join(random.choices(ALL_CHARS, k=length))
