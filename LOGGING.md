# MySLT Bot Logging System

The MySLT Bot project uses a robust structured logging system with the following features:

## Key Features

- **JSON structured logging**: All logs are formatted as JSON for easy parsing and analysis
- **Log rotation**: Logs automatically rotate based on size with retention policy
- **Separate error logs**: Critical and error logs are stored in dedicated files
- **Contextual information**: All logs include detailed context with timestamps, module, function, line numbers
- **Exception tracking**: Full exception details including traceback
- **Privacy protection**: Sensitive user data is partially masked in logs
- **Request IDs**: Correlation IDs for tracing requests across components
- **Event types**: Standard event type categorization for easy filtering and monitoring

## Directory Structure

Logs are stored in the `logs` directory with the following files:

- `discord_bot.log`: Main bot logs
- `discord_bot_error.log`: Error-only bot logs
- `api_server.log`: API server logs
- `api_server_error.log`: Error-only API server logs

## Common Event Types

The system uses standardized event types for consistent filtering:

### API Server
- `request_start`: API request received
- `request_complete`: API request completed
- `request_error`: API request failed
- `server_startup`: API server starting
- `server_shutdown`: API server shutting down
- `unhandled_exception`: Unexpected error

### Discord Bot
- `bot_ready`: Bot successfully connected
- `bot_disconnect`: Bot disconnected from Discord
- `bot_error`: Error in bot event
- `extension_loaded`: Bot extension loaded
- `extension_load_failed`: Failed to load extension
- `command_executed`: Command was executed
- `command_execution_error`: Error during command execution

### SLT API
- `slt_api_init`: API client initialized
- `slt_api_login_attempt`: Login attempt to SLT
- `slt_api_login_success`: Successful login
- `slt_api_login_failed`: Login failure
- `slt_api_request_start`: API request initiated
- `slt_api_request_success`: Successful API request
- `slt_api_http_error`: HTTP error from API
- `slt_api_token_refresh`: Token refresh operation

## Usage

The logging system is initialized automatically when the bot or API starts. The standard configuration can be modified via the `logging_config.py` file:

```python
# Example: Customize logging setup
logger = setup_logging(
    log_level=logging.DEBUG,  # Set log level
    app_name='custom_name',   # Change app name
    json_logs=False,          # Disable JSON logging
    log_dir='custom_logs'     # Change log directory
)
```

## Best Practices

1. **Use structured logging**: Always include the `extra` parameter with relevant context
2. **Include event types**: Always set the `event_type` field for easy filtering
3. **Mask sensitive data**: Never log full credentials, IDs, or personal information
4. **Use appropriate log levels**:
   - DEBUG: Detailed information for debugging
   - INFO: Confirmation that things are working
   - WARNING: Something unexpected but not critical
   - ERROR: Something failed but application continues
   - CRITICAL: Application cannot function

5. **Include correlation IDs**: Use request IDs to link related log entries 