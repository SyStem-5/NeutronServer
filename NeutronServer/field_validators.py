from django.core.exceptions import ValidationError


def validate_file_field(value):
    filesize = value.size
    
    # Check if filesize is over 3gb
    if filesize > 3221225472:
        raise ValidationError("The maximum file size that can be uploaded is 3GB")
    else:
        return value
