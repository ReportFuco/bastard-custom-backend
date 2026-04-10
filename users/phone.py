import re

from django.core.exceptions import ValidationError


CHILE_MOBILE_REGEX = re.compile(r"^569\d{8}$")


def normalize_chile_phone_number(value: str) -> str:
    raw_value = (value or "").strip()
    if not raw_value:
        return ""

    digits = re.sub(r"\D", "", raw_value)

    if digits.startswith("00"):
        digits = digits[2:]

    if digits.startswith("09") and len(digits) == 10:
        digits = "56" + digits[1:]
    elif digits.startswith("9") and len(digits) == 9:
        digits = "56" + digits

    if not CHILE_MOBILE_REGEX.fullmatch(digits):
        raise ValidationError(
            "Numero invalido. Debe ser celular chileno en formato 569XXXXXXXX."
        )

    return digits
