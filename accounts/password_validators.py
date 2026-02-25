
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class CustomPasswordValidator:
    def __init__(self):
        self.min_length = 8
        self.special_characters = r'[!@#$%^&*(),.?":{}|<>]'

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                _(f"Password must be at least {self.min_length} characters long."),
                code='password_too_short',
            )
        if not re.search(self.special_characters, password):
            raise ValidationError(
                _("Password must contain at least one special character (!@#$%^&*(),.?\":{}|<>)."),
                code='password_no_special_character',
            )
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _("Password must contain at least one uppercase letter."),
                code='password_no_uppercase',
            )
        if not re.search(r'[0-9]', password):
            raise ValidationError(
                _("Password must contain at least one number."),
                code='password_no_number',
            )

    def get_help_text(self):
        return _(
            f"Password must be at least {self.min_length} characters long, "
            "contain at least one special character (!@#$%^&*(),.?\":{}|<>), "
            "one uppercase letter, and one number."
        )