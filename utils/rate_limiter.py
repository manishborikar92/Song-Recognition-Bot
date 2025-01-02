import time
from functools import wraps

class RateLimiter:
    def __init__(self, limit: int, interval: int, exception_user_ids=None):
        """
        Initialize the rate limiter.
        
        :param limit: Maximum number of requests allowed.
        :param interval: Time window in seconds for the limit.
        :param exception_user_ids: List of user IDs to bypass the rate limiter.
        """
        self.limit = limit
        self.interval = interval
        self.requests = {}
        self.exception_user_ids = exception_user_ids or []

    def is_allowed(self, user_id: int) -> bool:
        """
        Check if the user is allowed to make a request.

        :param user_id: Unique identifier for the user.
        :return: True if allowed, False otherwise.
        """
        # Allow exception users to bypass rate limiting
        if user_id in self.exception_user_ids:
            return True

        current_time = time.time()
        if user_id not in self.requests:
            self.requests[user_id] = []

        # Remove expired requests
        self.requests[user_id] = [t for t in self.requests[user_id] if t > current_time - self.interval]

        if len(self.requests[user_id]) < self.limit:
            self.requests[user_id].append(current_time)
            return True

        return False

    def rate_limit_decorator(self, user_id_arg_name="user_id"):
        """
        Decorator to enforce rate limiting.

        :param user_id_arg_name: Name of the user ID argument in the wrapped function.
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Extract the user_id from the function's arguments
                user_id = kwargs.get(user_id_arg_name) or args[0].message.from_user.id
                if not self.is_allowed(user_id):
                    return await args[0].message.reply_text("❌ Rate limit exceeded. Please try again after 60 seconds.")

                return await func(*args, **kwargs)

            return wrapper

        return decorator
