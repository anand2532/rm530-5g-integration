"""Retry utilities for handling transient failures."""

import functools
import sys
import time
from typing import Callable, List, Optional, TypeVar, Union

if sys.version_info >= (3, 10):
    from typing import ParamSpec
else:
    from typing_extensions import ParamSpec

from rm530_5g_integration.utils.logging import get_logger

logger = get_logger(__name__)

P = ParamSpec("P")
T = TypeVar("T")


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 1.0,
    exceptions: Union[type[Exception], tuple[type[Exception], ...]] = Exception,
    on_failure: Optional[Callable[[Exception, int], None]] = None,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Decorator to retry a function on failure.

    Args:
        max_attempts: Maximum number of retry attempts (default: 3)
        delay: Initial delay between retries in seconds (default: 1.0)
        backoff: Multiplier for delay after each retry (default: 1.0)
        exceptions: Exception type(s) to catch and retry on
        on_failure: Optional callback called on each failure (exception, attempt_number)

    Returns:
        Decorated function

    Examples:
        >>> @retry(max_attempts=3, delay=1.0)
        ... def unreliable_function():
        ...     # May fail occasionally
        ...     pass
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            current_delay = delay
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if on_failure:
                        try:
                            on_failure(e, attempt)
                        except Exception:
                            pass  # Don't let failure handler break retry logic

                    if attempt < max_attempts:
                        logger.debug(
                            f"Retry attempt {attempt}/{max_attempts} for {func.__name__}: {e}"
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.warning(f"All {max_attempts} attempts failed for {func.__name__}")

            # Re-raise the last exception if all attempts failed
            raise last_exception

        return wrapper

    return decorator


def retry_with_backoff(
    max_attempts: int = 5,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
    exceptions: Union[type[Exception], tuple[type[Exception], ...]] = Exception,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Decorator to retry with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts (default: 5)
        initial_delay: Initial delay in seconds (default: 1.0)
        backoff_factor: Multiplier for exponential backoff (default: 2.0)
        max_delay: Maximum delay between retries in seconds (default: 60.0)
        exceptions: Exception type(s) to catch and retry on

    Returns:
        Decorated function

    Examples:
        >>> @retry_with_backoff(max_attempts=5, initial_delay=1.0, backoff_factor=2.0)
        ... def setup_modem():
        ...     # May need multiple attempts
        ...     pass
    """
    return retry(
        max_attempts=max_attempts,
        delay=initial_delay,
        backoff=backoff_factor,
        exceptions=exceptions,
        on_failure=lambda e, attempt: logger.info(
            f"Attempt {attempt} failed, retrying with exponential backoff: {e}"
        ),
    )


class RetryableError(Exception):
    """Exception that indicates an operation should be retried."""

    pass


class NonRetryableError(Exception):
    """Exception that indicates an operation should NOT be retried."""

    pass


def retry_on_retryable(
    max_attempts: int = 3, delay: float = 1.0, backoff: float = 1.0
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Decorator to retry only on RetryableError, not on NonRetryableError.

    This allows functions to signal which errors should trigger retries.

    Args:
        max_attempts: Maximum number of retry attempts (default: 3)
        delay: Initial delay between retries in seconds (default: 1.0)
        backoff: Multiplier for delay after each retry (default: 1.0)

    Returns:
        Decorated function
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            current_delay = delay

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except RetryableError as e:
                    if attempt < max_attempts:
                        logger.debug(f"Retryable error on attempt {attempt}/{max_attempts}: {e}")
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.warning(f"All {max_attempts} attempts failed (retryable errors)")
                        raise
                except NonRetryableError as e:
                    logger.error(f"Non-retryable error: {e}")
                    raise
                except Exception as e:
                    # Default: treat as non-retryable
                    raise

            # Should never reach here, but satisfy type checker
            raise RuntimeError("Unexpected retry state")

        return wrapper

    return decorator
