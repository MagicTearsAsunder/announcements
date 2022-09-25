from schema import Schema, And, SchemaError

schema = Schema(schema={
    'title': And(str, len),
    'description':  And(str, len),
})


def validate(data):
    global schema

    try:
        schema.validate(data)
    except SchemaError:
        return False
    else:
        return True
