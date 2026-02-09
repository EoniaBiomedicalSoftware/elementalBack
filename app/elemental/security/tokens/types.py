from app.elemental.common.enums.text import ElementalStrEnum


class ElementalTokenTypes(ElementalStrEnum):
    ACCESS = "access"
    REFRESH = "refresh"
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"
