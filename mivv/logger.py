import logging
import sys

def get_logger():
	logger = logging.getLogger()
	logger.setLevel(logging.WARN)
	log_format = '%(levelname)s: %(message)s'
	formatter = logging.Formatter(log_format)
	handler = logging.StreamHandler(sys.stderr)
	handler.setLevel(logging.DEBUG)
	handler.setFormatter(formatter)
	logger.addHandler(handler)
	return logger
