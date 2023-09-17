import logging
import logging.config

logger = logging.getLogger(__name__)

# load config from file
# logging.config.fileConfig('logging.ini', disable_existing_loggers=False)
# or, for dictConfig
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'stdout_fmt': {
            'format': '%(levelname)-8s %(message)s'
        }
    },
    'handlers': {
        'file_handler': {
            'level':'INFO',
            'class':'logging.FileHandler',
            'filename': 'output.log',
            'encoding': 'utf-8',
            'formatter': 'standard'
        },
        'default': {
            'level':'WARN',
            'class':'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'formatter': 'stdout_fmt'
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'WARN',
            'propagate': True
        },
        'file_logger': {
            'handlers': ['file_handler'],
            'level': 'INFO',
            'propagate': True
        },
    }
})
