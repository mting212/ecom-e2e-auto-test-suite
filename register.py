"""用户注册校验模块"""

def validate_password(password: str) -> str | None:
    """
    校验密码规则：8-20位，必须包含字母+数字
    返回 None 表示通过，否则返回错误提示
    """
    if len(password) < 8:
        return "密码长度不能少于8位"
    if len(password) > 20:
        return "密码长度不能超过20位"

    has_letter = any(c.isalpha() for c in password)
    has_digit = any(c.isdigit() for c in password)

    if not has_letter or not has_digit:
        return "密码需包含字母和数字"

    return None


def validate_phone(phone: str) -> str | None:
    if not phone:
        return "请输入手机号"
    if len(phone) != 11:
        return "手机号必须为11位"   # ← 走到这里就 return 了，后面不执行
    if not phone.isdigit():
        return "手机号必须为纯数字"  # ← 这行根本执行不到
    return None


def validate_nickname(nickname: str) -> str | None:
    """校验昵称：选填，填了就必须2-12字符"""
    if not nickname:
        return None  # 选填，不填不报错
    if len(nickname) < 2:
        return "昵称不能少于2个字符"
    if len(nickname) > 12:
        return "昵称不能超过12个字符"
    return None


def validate_confirm_password(password: str, confirm: str) -> str | None:
    """校验确认密码"""
    if not confirm:
        return "请再次输入密码"
    if password != confirm:
        return "两次密码输入不一致"
    return None
# ========== 以下是 Day 8 新增内容 ==========

class PhoneAlreadyRegisteredError(Exception):
    """自定义异常：手机号已注册"""
    pass


def validate_phone_raise(phone: str, registered_phones: list[str]) -> None:
    """
    校验手机号，不合法抛异常（和前面 return None 不同风格）
    - 格式不对 → ValueError
    - 已注册 → PhoneAlreadyRegisteredError
    - 通过 → 无返回（None）
    """
    if not phone:
        raise ValueError("请输入手机号")
    if len(phone) != 11:
        raise ValueError("手机号必须为11位")
    if not phone.isdigit():
        raise ValueError("手机号必须为纯数字")
    if phone in registered_phones:
        raise PhoneAlreadyRegisteredError(f"手机号 {phone} 已被注册")
    # 通过则什么都不返回