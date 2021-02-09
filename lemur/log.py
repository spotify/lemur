import datetime
import json
import logging
import sys


# Logging with renamed fields for StackDriver compatibility
def JsonFormatter(fields=None, **kwargs):
    class _cls(logging.Formatter):
        def __init__(self):
            super(_cls, self).__init__()

        def format(self, record):
            if fields:
                data = {kwargs.get(k, k): v for k, v in record.__dict__.items() if k in fields}
            else:
                data = {}

            data["timestamp"] = datetime.datetime.now().isoformat()
            data["message"] = record.getMessage()

            if record.exc_info:
                data["exc_info"] = self.formatException(record.exc_info)

            if record.stack_info:
                data["stack_info"] = self.formatStack(record.stack_info)

            return json.dumps(data)

    return _cls
