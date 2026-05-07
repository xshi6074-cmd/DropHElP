import hmac
import hashlib
import random
import string
from typing import Optional

try:
    from config import settings
except ImportError:
    from ..config import settings

def get_salted_hash(text: str) -> str:
    """生成加盐哈希，用于存储敏感数据(如验证码、教育邮箱)"""
    h = hmac.new(settings.secret_key.encode('utf-8'), text.encode('utf-8'), hashlib.sha256)
    return h.hexdigest()

def generate_random_code(length: int = 6, numeric_only: bool = True) -> str:
    """生成随机验证码"""
    if numeric_only:
        return ''.join(random.choices(string.digits, k=length))
    else:
        letters = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789" # 剔除了易混淆字符O,0,1,I
        return "".join(random.choice(letters) for _ in range(length))

def mask_email(email: str) -> str:
    """邮箱脱敏显示"""
    if '@' not in email:
        return email
    local, domain = email.split('@')
    if len(local) <= 2:
        return f"{local[0]}***@{domain}"
    return f"{local[:2]}***@{domain}"


def mask_phone(phone: str) -> str:
    """手机号脱敏显示"""
    if len(phone) != 11:
        return phone
    return f"{phone[:3]}****{phone[-4:]}"


def generate_hash_id(id_str: str) -> str:
    """生成hash_id用于信用追踪（隐私保护）"""
    import hashlib
    return hashlib.sha256(f"kuaibang:{id_str}".encode()).hexdigest()[:16]
