# Industry-Standard Logging Implementation Guide

## Overview

This document describes the logging architecture implemented in the RAG Chatbot application following industry best practices.

## Architecture

### Components

1. **Centralized Logging Configuration** (`backend/app/core/logging_config.py`)
   - JSON formatter for structured logging
   - Colored console formatter for development
   - Rotating file handler (10MB max, 5 backups)
   - Configurable log levels

2. **Request Logging Middleware** (`backend/app/middleware/logging_middleware.py`)
   - Automatic request ID generation
   - Request/response logging with timing
   - Error tracking with stack traces

3. **Service-Level Logging** (Throughout codebase)
   - Module-specific loggers
   - Contextual information
   - Performance metrics

## Features

### ✅ Implemented

- **Structured Logging**: JSON format for production, colored for development
- **Request Tracking**: Unique request IDs for tracing
- **Performance Monitoring**: Request duration tracking
- **Log Rotation**: Automatic file rotation to prevent disk fill
- **Contextual Information**: User ID, request ID, duration in logs
- **Error Tracking**: Full stack traces with context

### 📊 Log Levels

- **DEBUG**: Detailed information for diagnosing problems
- **INFO**: General informational messages
- **WARNING**: Warning messages for potentially harmful situations
- **ERROR**: Error messages for serious problems
- **CRITICAL**: Critical messages for very serious errors

## Configuration

### Environment Variables

```bash
# Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Enable JSON logging for production
JSON_LOGS=true
```

### Docker Compose

```yaml
environment:
  - LOG_LEVEL=INFO
  - JSON_LOGS=false  # Use colored logs in development
```

## Usage Examples

### Backend Logging

```python
import logging

logger = logging.getLogger(__name__)

# Info logging
logger.info("User logged in", extra={"user_id": user.id})

# Error logging with exception
try:
    process_document(file)
except Exception as e:
    logger.error("Document processing failed", exc_info=True, extra={"user_id": user.id})

# Debug logging
logger.debug(f"Retrieved {len(docs)} documents")
```

### Viewing Logs

```bash
# Real-time logs
docker logs -f rag_chatbot_backend

# Last 100 lines
docker logs --tail 100 rag_chatbot_backend

# Filter by level
docker logs rag_chatbot_backend 2>&1 | grep ERROR

# View log files
docker exec rag_chatbot_backend cat logs/app.log
```

## Log Format

### Development (Colored Console)
```
2025-01-03 16:30:45 | INFO     | app.main:startup:19 | Application started
2025-01-03 16:30:46 | INFO     | app.middleware.logging_middleware:dispatch:31 | Incoming request
```

### Production (JSON)
```json
{
  "timestamp": "2025-01-03T16:30:45.123456",
  "level": "INFO",
  "logger": "app.main",
  "message": "Application started",
  "module": "main",
  "function": "startup",
  "line": 19
}
```

### With Context
```json
{
  "timestamp": "2025-01-03T16:30:46.789012",
  "level": "INFO",
  "logger": "app.middleware.logging_middleware",
  "message": "Request completed",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "method": "POST",
  "path": "/chat/query",
  "status_code": 200,
  "duration_ms": 245.67
}
```

## Best Practices

### ✅ DO

- Use appropriate log levels
- Include contextual information (user_id, request_id)
- Log exceptions with `exc_info=True`
- Use structured logging in production
- Rotate log files to prevent disk fill
- Sanitize sensitive data before logging

### ❌ DON'T

- Log passwords or API keys
- Use print() statements
- Log in tight loops
- Include PII without sanitization
- Use DEBUG level in production

## Monitoring & Alerting

### Log Aggregation

For production, consider integrating with:
- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Splunk**
- **Datadog**
- **CloudWatch** (AWS)
- **Stackdriver** (GCP)

### Metrics to Monitor

- Error rate (ERROR/CRITICAL logs)
- Request duration (p50, p95, p99)
- Request volume
- Failed authentication attempts
- Document processing failures

## Troubleshooting

### Common Issues

**Issue**: Logs not appearing
- Check LOG_LEVEL environment variable
- Verify logging is initialized in main.py
- Check file permissions for log directory

**Issue**: Log files too large
- Adjust rotation settings in logging_config.py
- Reduce log level in production
- Implement log shipping to external service

**Issue**: Performance impact
- Use async logging for high-throughput
- Reduce DEBUG logging in production
- Use sampling for high-frequency events

## Future Enhancements

- [ ] Async logging for better performance
- [ ] Log sampling for high-frequency events
- [ ] Integration with OpenTelemetry
- [ ] Distributed tracing correlation
- [ ] Log shipping to external services
- [ ] Custom log metrics and dashboards

## References

- [Python Logging Documentation](https://docs.python.org/3/library/logging.html)
- [Twelve-Factor App: Logs](https://12factor.net/logs)
- [Structured Logging Best Practices](https://www.structlog.org/)
