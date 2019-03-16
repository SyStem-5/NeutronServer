from django.forms import ChoiceField

class ChoiceFieldIntegerNoValidation(ChoiceField):
    def valid_value(self, value):
        try:
            int(value)
        except TypeError:
            return False
        return True

class ChoiceFieldTextNoValidation(ChoiceField):
    def valid_value(self, value):
        return True