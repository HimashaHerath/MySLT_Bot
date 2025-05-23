import logging
import sys
import json
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import os
from datetime import datetime
import traceback

class JSONFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings after parsing the log record.
    """
    def __init__(self, fmt_dict=None):
        self.fmt_dict = fmt_dict if fmt_dict else {}
        super().__init__()
        
    def format(self, record):
        record_dict = self.__get_record_dict(record)
        return json.dumps(record_dict)
    
    def __get_record_dict(self, record):
        record_dict = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'name': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'process_id': record.process,
            'thread_id': record.thread
        }
        
        # Include exception info if available
        if record.exc_info:
            record_dict['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
            
        # Add any custom fields
        for key, value in self.fmt_dict.items():
            if hasattr(record, key):
                record_dict[key] = getattr(record, key)
                
        return record_dict

def setup_logging(
    log_level=logging.INFO,
    log_to_console=True,
    log_to_file=True,
    log_dir='logs',
    app_name='myslt',
    json_logs=True,
    max_bytes=10485760,  # 10MB
    backup_count=5
):
    """
    Set up logging with options for console and file output, JSON formatting, and rotation
    
    Args:
        log_level: Minimum log level to capture
        log_to_console: Whether to log to console
        log_to_file: Whether to log to file
        log_dir: Directory for log files
        app_name: Name of the application (used in log filenames)
        json_logs: Whether to format logs as JSON
        max_bytes: Maximum size of each log file
        backup_count: Number of backup files to keep
    """
    # Get the root logger
    logger = logging.getLogger()
    
    # Clear any existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Set the log level
    logger.setLevel(log_level)
    
    # Define text log format
    text_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s - %(message)s (%(filename)s:%(lineno)d)'
    )
    
    # Create JSON formatter
    json_formatter = JSONFormatter()
    
    # Create a console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(json_formatter if json_logs else text_formatter)
        logger.addHandler(console_handler)
    
    # Create a file handler with rotation
    if log_to_file:
        # Create log directory if it doesn't exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Daily rotation logs with a size limit
        log_file = os.path.join(log_dir, f"{app_name}.log")
        file_handler = RotatingFileHandler(
            log_file, 
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(json_formatter if json_logs else text_formatter)
        logger.addHandler(file_handler)
        
        # Create an error log file for ERROR and CRITICAL messages
        error_log_file = os.path.join(log_dir, f"{app_name}_error.log")
        error_file_handler = RotatingFileHandler(
            error_log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        error_file_handler.setLevel(logging.ERROR)
        error_file_handler.setFormatter(json_formatter if json_logs else text_formatter)
        logger.addHandler(error_file_handler)
    
    # Prevent message propagation to the root logger
    logger.propagate = False
    
    # Log initial message
    logger.info(f"Logging initialized for {app_name} application")
    
    return logger
