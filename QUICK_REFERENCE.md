# Quick Reference Guide

A quick reference for common patterns and best practices when building agents.

## Agent Patterns

### Reactive Agent (Simple & Fast)
```python
def process(input):
    if matches_pattern_A(input):
        return action_A()
    elif matches_pattern_B(input):
        return action_B()
    else:
        return default_action()
```

**Use when:** Quick responses needed, simple tasks, no state required

### Deliberative Agent (Planning)
```python
def process(input):
    state = analyze_situation(input)
    plan = create_plan(state, goals)
    for step in plan:
        execute(step)
    return result
```

**Use when:** Complex tasks, multi-step processes, future planning needed

### Hybrid Agent (Best of Both)
```python
def process(input):
    if is_urgent(input):
        return reactive_response(input)
    else:
        return deliberative_response(input)
```

**Use when:** Mix of simple and complex tasks, real-time constraints

## Essential Code Patterns

### Input Validation
```python
def validate_input(user_input):
    # Length check
    if not (MIN_LENGTH <= len(user_input) <= MAX_LENGTH):
        raise ValueError("Invalid length")
    
    # Pattern check
    if contains_injection_pattern(user_input):
        raise SecurityError("Suspicious input")
    
    # Sanitize
    return sanitize(user_input)
```

### Error Handling with Retry
```python
def with_retry(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except TransientError as e:
            if attempt < max_retries - 1:
                wait = 2 ** attempt
                time.sleep(wait)
            else:
                raise
        except PermanentError:
            raise  # Don't retry
```

### Structured Logging
```python
import logging
logger = logging.getLogger(__name__)

logger.info("event_occurred", extra={
    'event_type': 'processing',
    'user_id': user_id,
    'duration_ms': elapsed_time,
    'success': True
})
```

### Graceful Degradation
```python
def process_request(request):
    try:
        return primary_service(request)
    except ServiceError:
        logger.warning("Primary service failed, using fallback")
        return fallback_service(request)
    except Exception as e:
        logger.error(f"All services failed: {e}")
        return default_response()
```

## Security Checklist

- [ ] Validate all inputs (length, format, content)
- [ ] Check for injection patterns
- [ ] Use allowlists for commands
- [ ] Sanitize outputs
- [ ] Encrypt sensitive data
- [ ] Implement rate limiting
- [ ] Log security events
- [ ] Never expose internal errors to users

## Performance Checklist

- [ ] Cache frequently used data
- [ ] Use connection pooling
- [ ] Implement request batching
- [ ] Set appropriate timeouts
- [ ] Monitor response times
- [ ] Optimize prompt size
- [ ] Use streaming for long responses
- [ ] Profile and optimize bottlenecks

## Common Mistakes

| ❌ Don't | ✅ Do |
|---------|------|
| `except:` | `except SpecificError:` |
| Trust user input | Validate and sanitize |
| Ignore errors | Log and handle gracefully |
| Hard-code values | Use configuration |
| Skip logging | Log key events |
| Build monoliths | Use modular design |
| Forget to test | Write tests first |

## Testing Checklist

- [ ] Unit tests for core logic
- [ ] Integration tests for APIs
- [ ] End-to-end tests for workflows
- [ ] Edge case testing
- [ ] Error condition testing
- [ ] Load/stress testing
- [ ] Security testing

## Monitoring Essentials

### Key Metrics
```python
metrics_to_track = {
    'response_time_ms': timer.elapsed(),
    'success_rate': successes / total,
    'error_rate': errors / total,
    'tokens_used': token_count,
    'cost_per_request': cost,
}
```

### Health Check
```python
def health_check():
    return {
        'status': 'healthy',
        'uptime': get_uptime(),
        'dependencies': check_dependencies(),
        'metrics': get_current_metrics()
    }
```

## Quick Debugging

### Enable Debug Logging
```python
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Add Trace IDs
```python
trace_id = str(uuid.uuid4())
logger.info("request_started", extra={'trace_id': trace_id})
# ... processing ...
logger.info("request_completed", extra={'trace_id': trace_id})
```

### Profile Performance
```python
import time

start = time.time()
result = expensive_operation()
elapsed = time.time() - start

if elapsed > THRESHOLD:
    logger.warning(f"Slow operation: {elapsed}s")
```

## Configuration Template

```python
CONFIG = {
    # Limits
    'max_input_length': 10000,
    'max_output_length': 5000,
    'request_timeout': 30,
    
    # Retry
    'max_retries': 3,
    'retry_delay': 1.0,
    
    # Rate Limiting
    'requests_per_minute': 60,
    'burst_size': 10,
    
    # Features
    'enable_caching': True,
    'cache_ttl': 300,
    'enable_logging': True,
    
    # Security
    'require_auth': True,
    'allowed_origins': ['https://example.com'],
}
```

## Response Template

```python
def create_response(success, data=None, error=None):
    return {
        'success': success,
        'data': data,
        'error': error,
        'timestamp': datetime.utcnow().isoformat(),
        'version': API_VERSION
    }

# Success
return create_response(True, data={'result': result})

# Error
return create_response(False, error={'message': 'Error occurred'})
```

## API Client Pattern

```python
class ExternalAPIClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()
    
    def call(self, endpoint, data):
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = self.session.post(
                url,
                json=data,
                headers={'Authorization': f'Bearer {self.api_key}'},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.Timeout:
            raise TransientError("Request timeout")
        except requests.HTTPError as e:
            if e.response.status_code >= 500:
                raise TransientError("Server error")
            else:
                raise PermanentError(f"Client error: {e}")
```

## State Management

```python
from dataclasses import dataclass, replace

@dataclass(frozen=True)  # Immutable
class AgentState:
    user_id: str
    conversation_id: str
    context: dict
    turn_count: int = 0
    
    def update(self, **changes):
        """Create new state with updates"""
        return replace(self, **changes)

# Usage
state = AgentState(user_id='123', conversation_id='abc', context={})
new_state = state.update(turn_count=state.turn_count + 1)
```

## Context Window Management

```python
def manage_context(messages, max_tokens=4000):
    """Keep context within token limit"""
    total_tokens = sum(count_tokens(msg) for msg in messages)
    
    if total_tokens <= max_tokens:
        return messages
    
    # Keep system message and recent messages
    return [
        messages[0],  # System message
        *messages[-(max_tokens // 100):]  # Recent messages
    ]
```

## Common Regex Patterns

```python
PATTERNS = {
    'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    'url': r'^https?://[^\s<>"{}|\\^`\[\]]+$',
    'phone': r'^\+?1?\d{9,15}$',
    'sql_injection': r"('|(--)|;|\b(union|select|insert|update|delete|drop)\b)",
    'script_tag': r'<script[^>]*>.*?</script>',
}
```

## Resource Limits

```python
import resource
import signal

# Set memory limit (100 MB)
resource.setrlimit(resource.RLIMIT_AS, (100 * 1024 * 1024, -1))

# Set CPU time limit (10 seconds)
resource.setrlimit(resource.RLIMIT_CPU, (10, 10))

# Timeout decorator
def timeout(seconds):
    def decorator(func):
        def handler(signum, frame):
            raise TimeoutError()
        
        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(seconds)
            try:
                return func(*args, **kwargs)
            finally:
                signal.alarm(0)
        return wrapper
    return decorator
```

---

For detailed explanations and more examples, see [BEST_PRACTICES.md](BEST_PRACTICES.md)
