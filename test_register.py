"""注册页校验测试用例 —— 参数化改造版"""
import pytest
from register import (
    validate_password,
    validate_phone,
    validate_nickname,
    validate_confirm_password,
)


# ========== 密码长度 ==========
@pytest.mark.parametrize("password, expected", [
    ("Abc1234",  "密码长度不能少于8位"),       # 7位
    ("Abc12345", None),                        # 8位
    ("Abc12345678901234567", None),            # 20位
    ("Abc123456789012345678", "密码长度不能超过20位"),  # 21位
])
def test_password_length(password, expected):
    result = validate_password(password)
    assert result == expected


# ========== 密码组合 ==========
@pytest.mark.parametrize("password, expected", [
    ("12345678",   "密码需包含字母和数字"),     # 纯数字
    ("abcdefgh",   "密码需包含字母和数字"),     # 纯字母
    ("!@#$%^&*",   "密码需包含字母和数字"),     # 纯特殊字符（取决于规则）
])
def test_password_composition(password, expected):
    result = validate_password(password)
    assert result == expected


# ========== 手机号 ==========
@pytest.mark.parametrize("phone, expected", [
    ("13900139000",  None),                   # 11位合规
    ("",             "请输入手机号"),           # 为空
    ("1390013900",   "手机号必须为11位"),       # 10位
    ("139001390000", "手机号必须为11位"),       # 12位
    ("1390013900a",  "手机号必须为纯数字"),     # 含字母
])
def test_phone(phone, expected):
    result = validate_phone(phone)
    assert result == expected


# ========== 确认密码 ==========
@pytest.mark.parametrize("password, confirm, expected", [
    ("Aa123456", "Aa123456", None),
    ("Aa123456", "Aa123457", "两次密码输入不一致"),
    ("Aa123456", "",         "请再次输入密码"),
])
def test_confirm_password(password, confirm, expected):
    result = validate_confirm_password(password, confirm)
    assert result == expected


# ========== 昵称 ==========
@pytest.mark.parametrize("nickname, expected", [
    ("测试昵称",       None),
    ("",               None),                 # 选填，不报错
    ("A",              "昵称不能少于2个字符"),
    ("1234567890123",  "昵称不能超过12个字符"),
])
def test_nickname(nickname, expected):
    result = validate_nickname(nickname)
    assert result == expected
# ========== fixture 演示：完整注册流程 ==========

@pytest.fixture
def valid_user():
    """一个合规用户数据，复用"""
    return {
        "phone": "13900139000",
        "password": "Aa123456",
        "confirm": "Aa123456",
        "nickname": "测试用户",
    }


def test_full_register_all_pass(valid_user):
    """全部字段合规 → 四个校验都通过"""
    assert validate_phone(valid_user["phone"]) is None
    assert validate_password(valid_user["password"]) is None
    assert validate_confirm_password(
        valid_user["password"], valid_user["confirm"]
    ) is None
    assert validate_nickname(valid_user["nickname"]) is None
    assert validate_confirm_password(
        valid_user["password"], valid_user["confirm"]
    ) is None
    assert validate_nickname(valid_user["nickname"]) is None


def test_full_register_password_mismatch(valid_user):
    """确认密码不一致 → 只有确认密码报错，其他通过"""
    assert validate_phone(valid_user["phone"]) is None
    assert validate_password(valid_user["password"]) is None
    assert validate_confirm_password(
        valid_user["password"], "WrongPass"
    ) == "两次密码输入不一致"
    assert validate_nickname(valid_user["nickname"]) is None
# ========== Day 8：异常测试 ==========
from register import validate_phone_raise, PhoneAlreadyRegisteredError


# 存放已注册手机号的 fixture
@pytest.fixture
def registered_phones():
    return ["13800001111", "13800002222"]


def test_phone_raise_valid(registered_phones):
    """合规手机号 → 不抛异常，正常执行完"""
    validate_phone_raise("13900139000", registered_phones)
    # 没抛异常 = 通过，不需要 assert


def test_phone_raise_empty(registered_phones):
    """空手机号 → 抛 ValueError"""
    with pytest.raises(ValueError, match="请输入手机号"):
        validate_phone_raise("", registered_phones)


def test_phone_raise_wrong_length(registered_phones):
    """位数不对 → 抛 ValueError"""
    with pytest.raises(ValueError, match="手机号必须为11位"):
        validate_phone_raise("12345", registered_phones)


def test_phone_raise_not_digit(registered_phones):
    """含字母 → 抛 ValueError"""
    with pytest.raises(ValueError, match="手机号必须为纯数字"):
        validate_phone_raise("1390013900a", registered_phones)


def test_phone_raise_already_registered(registered_phones):
    """已注册 → 抛自定义异常"""
    with pytest.raises(PhoneAlreadyRegisteredError, match="已被注册"):
        validate_phone_raise("13800001111", registered_phones)