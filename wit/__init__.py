from wit import Wit

import logging
# set a NullLogger so logger will not output to stderror in the
# case that the client app doesnt configure logging.
try:
    logging.getLogger(__name__).addHandler(logging.NullHandler())
except AttributeError:
    # NullHandler added in python 2.7, use custom handler for older versions
    class CustomNullHandler(logging.Handler):
        def emit(self, record):
            pass
    logging.getLogger(__name__).addHandler(CustomNullHandler())
