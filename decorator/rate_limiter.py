import time
from functools import wraps

class RateLimiter:
    def __init__(self, limit: int, interval: int, exception_user_ids=None):
        self.limit = limit
        self.interval = interval
        self.requests = {}
        self.exception_user_ids = exception_user_ids or []

    def is_allowed(self, user_id: int):
        if user_id in self.exception_user_ids:
            return True, 0  # No limit for exception users

        current_time = time.time()
        if user_id not in self.requests:
            self.requests[user_id] = []

        # Remove expired requests
        self.requests[user_id] = [t for t in self.requests[user_id] if t > current_time - self.interval]

        if len(self.requests[user_id]) < self.limit:
            self.requests[user_id].append(current_time)
            return True, 0  # Request allowed, no wait time

        # Calculate the time remaining until the user can make another request
        next_allowed_time = self.requests[user_id][0] + self.interval
        remaining_time = max(0, next_allowed_time - current_time)
        return False, remaining_time  # Rate limit exceeded, return remaining time

    def rate_limit_decorator(self, user_id_arg_name="user_id"):
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                user_id = kwargs.get(user_id_arg_name) or args[0].message.from_user.id
                allowed, remaining_time = self.is_allowed(user_id)

                if not allowed:
                    remaining_seconds = int(remaining_time)  # Get the remaining time in seconds
                    return await args[0].message.reply_text(
                        f"❌ Rate limit exceeded. Please try again after {remaining_seconds}s."
                    )

                return await func(*args, **kwargs)

            return wrapper

        return decorator
