import json

def escapejs(value):
    """
    Escape a string for use in JavaScript/JSON.
    This is similar to Django's escapejs filter.
    """
    if value is None:
        return ''
    return json.dumps(str(value))[1:-1]  # Remove the surrounding quotes from json.dumps
