from flask_restful import fields


class DateTimeFormat(fields.Raw):
    def format(self, value):
        return value.__str__()