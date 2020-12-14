import logging
import datetime
from pythonjsonlogger.jsonlogger import JsonFormatter

root = logging.getLogger(__name__)
root = logging.getLogger()
root.setLevel(logging.INFO)

sh = logging.StreamHandler()

# log_format= dict([
#     ('asctime', 'asctime'),
#     ('name', 'name'),
#     ('levelname', 'levelname'),
#     ('message', 'message')])
#
# formatter = JsonFormatter(
#     fmt=log_format,
#     ensure_ascii=False,
#     mix_extra=True,
#     mix_extra_position='tail' # optional: head, mix
# )

log_format = '%(asctime)%(name)%(levelname):%(message)'
formatter = JsonFormatter(log_format)

sh.setFormatter(formatter)
sh.setLevel(logging.INFO)
root.addHandler(sh)

for logg in [logging.getLogger()] + [logging.getLogger(name) for name in logging.root.manager.loggerDict]:
    print(logg.name, logg.handlers)


root.info(
    'test mix extra in fmt',
    extra={
        'extra1': 'extra content 1',
        'extra2': 'extra content 2'
    })
root.info(
    'test mix extra in fmt',
    extra={
        'extra3': 'extra content 3',
        'extra4': 'extra content 4'
    })