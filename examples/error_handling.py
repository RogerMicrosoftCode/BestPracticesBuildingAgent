"""
Error Handling Best Practices for Agents

Demonstrates comprehensive error handling patterns including:
- Graceful degradation
- Retry logic with exponential backoff
- Fallback behaviors
- Error categorization
- Detailed logging
"""

import time
import random
from typing import Optional, Callable, Any, Dict
from dataclasses import dataclass
from enum import Enum
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Categorize errors by severity"""
    LOW = "low"              # Minor issues, can continue
    MEDIUM = "medium"        # Significant issues, may need fallback
    HIGH = "high"           # Critical issues, requires immediate attention
    CRITICAL = "critical"   # System failure, emergency shutdown


class ErrorCategory(Enum):
    """Categorize errors by type"""
    TRANSIENT = "transient"      # Temporary, retry may succeed
    PERMANENT = "permanent"       # Persistent, retry will fail
    VALIDATION = "validation"     # Invalid input/data
    EXTERNAL = "external"         # External service failure
    INTERNAL = "internal"         # Internal system error


@dataclass
class ErrorContext:
    """Context information about an error"""
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    details: Dict[str, Any]
    retry_count: int = 0


class TransientError(Exception):
    """Temporary error that may succeed on retry"""
    pass


class PermanentError(Exception):
    """Permanent error that will not succeed on retry"""
    pass


class ValidationError(Exception):
    """Input validation error"""
    pass


class ExternalServiceError(Exception):
    """External service error"""
    pass


def with_retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0
):
    """
    Decorator for retry logic with exponential backoff.
    
    Best Practices:
    1. Exponential backoff to avoid overwhelming failing services
    2. Maximum delay cap to prevent excessive waiting
    3. Configurable retry attempts
    4. Logging of retry attempts
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                    
                except TransientError as e:
                    last_exception = e
                    
                    if attempt < max_retries - 1:
                        # Calculate delay with exponential backoff
                        delay = min(
                            base_delay * (exponential_base ** attempt),
                            max_delay
                        )
                        
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries} failed: {e}. "
                            f"Retrying in {delay:.2f}s..."
                        )
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"All {max_retries} attempts failed: {e}"
                        )
                
                except PermanentError as e:
                    logger.error(f"Permanent error, not retrying: {e}")
                    raise
                
                except Exception as e:
                    logger.error(f"Unexpected error: {e}")
                    raise
            
            # If we get here, all retries failed
            raise last_exception
        
        return wrapper
    return decorator


class ErrorHandler:
    """
    Centralized error handling for agent operations.
    
    Best Practices Demonstrated:
    1. Error categorization
    2. Severity assessment
    3. Appropriate retry logic
    4. Fallback behaviors
    5. Comprehensive logging
    """
    
    def __init__(self):
        self.error_counts: Dict[str, int] = {}
        self.fallback_responses = {
            ErrorCategory.EXTERNAL: "I'm having trouble reaching external services. Please try again later.",
            ErrorCategory.VALIDATION: "I couldn't understand that input. Please rephrase.",
            ErrorCategory.INTERNAL: "I encountered an internal error. Please try again.",
            ErrorCategory.TRANSIENT: "Service temporarily unavailable. Please retry.",
            ErrorCategory.PERMANENT: "This operation cannot be completed. Please contact support."
        }
    
    def handle_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> ErrorContext:
        """
        Handle an error with appropriate categorization and response.
        
        Args:
            error: The exception that occurred
            context: Additional context about where/why the error occurred
            
        Returns:
            ErrorContext with categorized error information
        """
        # Categorize the error
        category = self._categorize_error(error)
        severity = self._assess_severity(error, category)
        
        # Create error context
        error_context = ErrorContext(
            category=category,
            severity=severity,
            message=str(error),
            details=context or {}
        )
        
        # Log the error
        self._log_error(error_context)
        
        # Track error statistics
        self._track_error(error_context)
        
        return error_context
    
    def _categorize_error(self, error: Exception) -> ErrorCategory:
        """Categorize error by type"""
        if isinstance(error, TransientError):
            return ErrorCategory.TRANSIENT
        elif isinstance(error, PermanentError):
            return ErrorCategory.PERMANENT
        elif isinstance(error, ValidationError):
            return ErrorCategory.VALIDATION
        elif isinstance(error, ExternalServiceError):
            return ErrorCategory.EXTERNAL
        else:
            return ErrorCategory.INTERNAL
    
    def _assess_severity(
        self,
        error: Exception,
        category: ErrorCategory
    ) -> ErrorSeverity:
        """Assess error severity"""
        # Map categories to typical severities
        severity_map = {
            ErrorCategory.TRANSIENT: ErrorSeverity.LOW,
            ErrorCategory.VALIDATION: ErrorSeverity.LOW,
            ErrorCategory.EXTERNAL: ErrorSeverity.MEDIUM,
            ErrorCategory.PERMANENT: ErrorSeverity.HIGH,
            ErrorCategory.INTERNAL: ErrorSeverity.HIGH,
        }
        
        return severity_map.get(category, ErrorSeverity.MEDIUM)
    
    def _log_error(self, error_context: ErrorContext):
        """Log error with appropriate level"""
        log_message = (
            f"[{error_context.category.value}] "
            f"{error_context.message} "
            f"(severity: {error_context.severity.value})"
        )
        
        if error_context.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message, extra=error_context.details)
        elif error_context.severity == ErrorSeverity.HIGH:
            logger.error(log_message, extra=error_context.details)
        elif error_context.severity == ErrorSeverity.MEDIUM:
            logger.warning(log_message, extra=error_context.details)
        else:
            logger.info(log_message, extra=error_context.details)
    
    def _track_error(self, error_context: ErrorContext):
        """Track error statistics"""
        key = f"{error_context.category.value}_{error_context.severity.value}"
        self.error_counts[key] = self.error_counts.get(key, 0) + 1
    
    def get_fallback_response(self, error_context: ErrorContext) -> str:
        """Get appropriate fallback response for error"""
        return self.fallback_responses.get(
            error_context.category,
            "An error occurred. Please try again."
        )
    
    def should_retry(self, error_context: ErrorContext) -> bool:
        """Determine if operation should be retried"""
        return error_context.category in [
            ErrorCategory.TRANSIENT,
            ErrorCategory.EXTERNAL
        ]


class ResilientAgent:
    """
    Agent with comprehensive error handling.
    
    Demonstrates:
    1. Graceful degradation
    2. Retry logic
    3. Fallback behaviors
    4. Error recovery
    """
    
    def __init__(self):
        self.error_handler = ErrorHandler()
    
    @with_retry(max_retries=3, base_delay=1.0)
    def process_with_retry(self, task: str) -> str:
        """Process task with automatic retry on transient errors"""
        # Simulate processing that might fail transiently
        if random.random() < 0.3:  # 30% chance of transient failure
            raise TransientError("Temporary service unavailable")
        
        return f"Processed: {task}"
    
    def process_safely(self, task: str) -> str:
        """
        Process task with comprehensive error handling.
        
        This method demonstrates the full error handling pattern:
        1. Try primary operation
        2. Catch and categorize errors
        3. Determine retry strategy
        4. Provide fallback response
        """
        try:
            # Validate input
            if not task or len(task) > 1000:
                raise ValidationError("Invalid task input")
            
            # Try primary processing
            result = self.process_with_retry(task)
            return result
            
        except ValidationError as e:
            context = self.error_handler.handle_error(
                e,
                context={'task': task, 'operation': 'validation'}
            )
            return self.error_handler.get_fallback_response(context)
        
        except TransientError as e:
            context = self.error_handler.handle_error(
                e,
                context={'task': task, 'operation': 'processing'}
            )
            # After retries exhausted, use fallback
            return self.error_handler.get_fallback_response(context)
        
        except PermanentError as e:
            context = self.error_handler.handle_error(
                e,
                context={'task': task, 'operation': 'processing'}
            )
            return self.error_handler.get_fallback_response(context)
        
        except Exception as e:
            context = self.error_handler.handle_error(
                e,
                context={
                    'task': task,
                    'operation': 'processing',
                    'unexpected': True
                }
            )
            # For unexpected errors, use safe fallback
            return "An unexpected error occurred. Our team has been notified."
    
    def get_error_statistics(self) -> Dict[str, int]:
        """Get error statistics for monitoring"""
        return self.error_handler.error_counts.copy()


def main():
    """Demonstrate error handling patterns"""
    agent = ResilientAgent()
    
    print("Error Handling Demo")
    print("=" * 70)
    
    # Test cases
    test_tasks = [
        "valid task 1",
        "valid task 2",
        "valid task 3",
        "",  # Invalid - empty
        "x" * 1500,  # Invalid - too long
    ]
    
    for task in test_tasks:
        task_preview = task[:50] + "..." if len(task) > 50 else task
        print(f"\nTask: '{task_preview}'")
        
        result = agent.process_safely(task)
        print(f"Result: {result}")
    
    # Show error statistics
    print("\n" + "=" * 70)
    print("\nError Statistics:")
    stats = agent.get_error_statistics()
    for error_type, count in stats.items():
        print(f"  {error_type}: {count}")
    
    print("\n" + "=" * 70)
    print("\nBest Practices Demonstrated:")
    print("1. ✓ Error categorization (transient, permanent, validation)")
    print("2. ✓ Retry logic with exponential backoff")
    print("3. ✓ Graceful degradation with fallbacks")
    print("4. ✓ Comprehensive error logging")
    print("5. ✓ Error statistics tracking")
    print("6. ✓ User-friendly error messages")


if __name__ == "__main__":
    main()
