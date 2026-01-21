from rest_framework.throttling import UserRateThrottle


class UserMeThrottle(UserRateThrottle):
    """Throttle for user profile endpoint."""

    scope = "user_me"
    rate = "60/minute"
