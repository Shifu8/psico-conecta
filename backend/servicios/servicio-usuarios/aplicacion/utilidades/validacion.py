import re

from marshmallow import ValidationError


NAME_PATTERN = re.compile(r"^[^\W\d_]+(?:[ '-][^\W\d_]+)*$", re.UNICODE)
PHONE_PATTERN = re.compile(r"^\+?[0-9][0-9 ()-]*[0-9]$")
ROLE_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")
SPECIAL_CHARACTER_PATTERN = re.compile(r"[^\w\s]", re.UNICODE)
WEAK_PASSWORDS = {
    "12345678",
    "admin123*",
    "contraseña123*",
    "password123*",
    "psicoconecta123*",
    "qwerty123*",
}
PASSWORD_MESSAGE = (
    "La contraseña debe tener entre 8 y 128 caracteres, una mayúscula, "
    "una minúscula, un número y un carácter especial, sin espacios."
)


def normalize_spaces(value):
    return " ".join(value.strip().split()) if isinstance(value, str) else value


def normalize_email(value):
    return value.strip().lower() if isinstance(value, str) else value


def normalize_phone(value):
    if value is None:
        return None
    value = normalize_spaces(value)
    return value or None


def validate_name(value):
    if not NAME_PATTERN.fullmatch(value):
        raise ValidationError(
            "Usa únicamente letras, espacios, apóstrofes o guiones."
        )


def validate_phone(value):
    if value is None:
        return
    digits = re.sub(r"\D", "", value)
    if (
        not PHONE_PATTERN.fullmatch(value)
        or not 7 <= len(digits) <= 15
        or len(value) > 20
    ):
        raise ValidationError(
            "Ingresa un teléfono válido de 7 a 15 dígitos."
        )


def validate_password(value):
    if (
        not 8 <= len(value) <= 128
        or any(character.isspace() for character in value)
        or not any(character.isupper() for character in value)
        or not any(character.islower() for character in value)
        or not any(character.isdigit() for character in value)
        or not SPECIAL_CHARACTER_PATTERN.search(value)
        or value.lower() in WEAK_PASSWORDS
        or len(set(value.lower())) < 5
    ):
        raise ValidationError(PASSWORD_MESSAGE)


def validate_role_name(value):
    if not ROLE_PATTERN.fullmatch(value):
        raise ValidationError(
            "Usa únicamente letras, números, guiones o guiones bajos."
        )
