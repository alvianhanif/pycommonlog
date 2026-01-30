# pycommonlog

[![CI](https://github.com/alvianhanif/pycommonlog/actions/workflows/ci.yml/badge.svg)](https://github.com/alvianhanif/pycommonlog/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/pycommonlog)](https://pypi.org/project/pycommonlog/)
[![Python versions](https://img.shields.io/pypi/pyversions/pycommonlog)](https://pypi.org/project/pycommonlog/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A unified logging and alerting library for Python, supporting Slack and Lark integrations via WebClient and Webhook. Features configurable providers, alert levels, and file attachment support.

## Installation

Install via pip:

```bash
pip install pycommonlog
```

Or copy the `pycommonlog/` directory to your project.


## Usage

```python
from pycommonlog import commonlog, Config, SendMethod, AlertLevel, Attachment, LarkToken

# Configure logger
config = Config(
    send_method=SendMethod.WEBCLIENT,
    channel="your_lark_channel_id",
    provider_config={
        "provider": "lark", # or "slack"
        "token": "app_id++app_secret", # for Lark, use "app_id++app_secret" format
        "slack_token": "xoxb-your-slack-token", # dedicated Slack token
        "lark_token": LarkToken(app_id="your-app-id", app_secret="your-app-secret"), # dedicated Lark token
        "redis_host": "localhost",  # required for Lark
        "redis_port": 6379,         # required for Lark
    }
)
logger = commonlog(config)

# Send error with attachment
try:
    logger.send(AlertLevel.ERROR, "System error occurred", Attachment(url="https://example.com/log.txt"))
except Exception as e:
    print(f"Failed to send alert: {e}")

 # Send info (logs only)
logger.send(AlertLevel.INFO, "Info message")

# Send to a specific channel
try:
    logger.send_to_channel(AlertLevel.ERROR, "Send to another channel", channel="another-channel-id")
except Exception as e:
    print(f"Failed to send alert: {e}")

# Send to a different provider dynamically
try:
    logger.custom_send("slack", AlertLevel.ERROR, "Message via Slack", channel="slack-channel")
except Exception as e:
    print(f"Failed to send alert: {e}")
```

## Send Methods

commonlog supports two send methods: WebClient (API-based) and Webhook (simple HTTP POST).

### WebClient Usage

WebClient uses the full API with authentication tokens:

```python
config = Config(
    send_method=SendMethod.WEBCLIENT,
    channel="your_channel",
    provider_config={
        "provider": "lark",  # or "slack"
        "token": "app_id++app_secret",  # for Lark
        "slack_token": "xoxb-your-slack-token",  # for Slack
        "lark_token": LarkToken(app_id="your-app-id", app_secret="your-app-secret"),
        "redis_host": "localhost",  # required for Lark
        "redis_port": 6379,         # required for Lark
    }
)
```

### Webhook Usage

Webhook is simpler and requires only a webhook URL:

```python
config = Config(
    send_method=SendMethod.WEBHOOK,
    channel="optional-channel-override",  # optional
    provider_config={
        "provider": "slack",
        "token": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
    }
)
```

### Lark Token Configuration

Lark integration requires proper token configuration for authentication. You can configure Lark tokens in two ways:

#### Method 1: Combined Token Format

```python
config = Config(
    send_method=SendMethod.WEBCLIENT,
    channel="your_channel_id",
    provider_config={
        "provider": "lark",
        "token": "your_app_id++your_app_secret",  # Combined format: app_id++app_secret
        "redis_host": "localhost",  # Optional: enables caching
        "redis_port": 6379,
    }
)
```

#### Method 2: Dedicated Lark Token Object

```python
config = Config(
    send_method=SendMethod.WEBCLIENT,
    channel="your_channel_id",
    provider_config={
        "provider": "lark",
        "lark_token": LarkToken(
            app_id="your_app_id",
            app_secret="your_app_secret"
        ),
        "redis_host": "localhost",  # Optional: enables caching
        "redis_port": 6379,
    }
)
```

### Lark Token Caching

When using Lark, the `tenant_access_token` is cached to reduce API calls and improve performance. The library supports both Redis and in-memory caching:

- **Redis Caching** (recommended for production): Persistent across application restarts and shared between instances
- **In-Memory Caching** (fallback): Automatic fallback when Redis is unavailable, with 90-minute token expiry

**Token Expiry Details:**

- API tokens expire after 2 hours (7200 seconds)
- Cached tokens expire after 90 minutes (5400 seconds) to ensure freshness
- Chat ID mappings are cached for 30 days

**Cache Keys:**

- Lark tokens: `commonlog_lark_token:{app_id}:{app_secret}`
- Chat IDs: `commonlog_lark_chat_id:{environment}:{channel_name}`

See [REDIS_SETUP.md](REDIS_SETUP.md) for detailed Redis setup instructions including AWS ElastiCache configuration.

## Channel Mapping

You can configure different channels for different alert levels using a channel resolver:

```python
from commonlog import commonlog, Config, SendMethod, AlertLevel, DefaultChannelResolver

# Create a channel resolver
resolver = DefaultChannelResolver(
    channel_map={
        AlertLevel.INFO: "#general",
        AlertLevel.WARN: "#warnings",
        AlertLevel.ERROR: "#alerts",
    },
    default_channel="#general"
)

# Create config with channel resolver
config = Config(
    send_method=SendMethod.WEBCLIENT,
    channel_resolver=resolver,
    service_name="user-service",
    environment="production",
    provider_config={
        "provider": "slack",
        "token": "xoxb-your-slack-bot-token",
    }
)

logger = commonlog(config)

# These will go to different channels based on level
logger.send(AlertLevel.INFO, "Info message")    # goes to #general
logger.send(AlertLevel.WARN, "Warning message") # goes to #warnings
logger.send(AlertLevel.ERROR, "Error message")  # goes to #alerts
```

### Custom Channel Resolver

You can implement custom channel resolution logic:

```python
class CustomResolver(ChannelResolver):
    def resolve_channel(self, level):
        if level == AlertLevel.ERROR:
            return "#critical-alerts"
        elif level == AlertLevel.WARN:
            return "#monitoring"
        else:
            return "#general"
```

## Configuration Options

### Common Settings

- **send_method**: `"webclient"` (token-based authentication) or `"webhook"`
- **channel**: Target channel or chat ID (used if no resolver)
- **channel_resolver**: Optional resolver for dynamic channel mapping
- **service_name**: Name of the service sending alerts
- **environment**: Environment (dev, staging, production)
- **debug**: `True` to enable detailed debug logging of all internal processes

### ProviderConfig Settings

All provider-specific configuration is now done via the `provider_config` dict:

- **provider**: `"slack"` or `"lark"`
- **token**: API token for WebClient authentication or webhook URL for Webhook method
- **slack_token**: Dedicated Slack token (optional, overrides token for Slack)
- **lark_token**: `LarkToken` object with app_id and app_secret (optional, overrides token for Lark)
- **redis_host**: Redis host for Lark caching (optional)
- **redis_port**: Redis port for Lark caching (optional)
- **redis_password**: Redis password (optional)
- **redis_ssl**: Enable SSL for Redis (optional)
- **redis_cluster_mode**: Enable Redis cluster mode (optional)
- **redis_db**: Redis database number (optional)

## Alert Levels

- **INFO**: Logs locally only
- **WARN**: Logs + sends alert
- **ERROR**: Always sends alert

## File Attachments

Provide a public URL. The library appends it to the message for simplicity.

```python
attachment = Attachment(url="https://example.com/log.txt")
logger.send(AlertLevel.ERROR, "Error with log", attachment)
```

## Trace Log Section

When `include_trace` is set to `True`, you can pass trace information as the fourth parameter to `send()`:

```python
trace = """Traceback (most recent call last):
  File "app.py", line 10, in main
    raise ValueError("Something went wrong")
ValueError: Something went wrong"""

logger.send(AlertLevel.ERROR, "System error occurred", None, trace)
```

This will format the trace as a code block in the alert message.

## Testing

```bash
python -m pytest test_commonlog.py
```

## API Reference

### Classes

- `Config`: Configuration class
- `Attachment`: File attachment class
- `Provider`: Abstract base class for alert providers
- `commonlog`: Main logger class

### Constants

- `SendMethod.WEBCLIENT`: Send method (token-based authentication)
- `AlertLevel.INFO`, `AlertLevel.WARN`, `AlertLevel.ERROR`: Alert levels

### Methods

- `commonlog(config)`: Create a new logger
- `commonlog.send(level, message, attachment=None, trace="")`: Send alert with optional trace
