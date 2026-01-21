from rest_framework.throttling import AnonRateThrottle


class SignInThrottle(AnonRateThrottle):
    """
    Strict throttle for sign-in endpoint to prevent brute force attacks.
    5 attempts per minute per IP.
    """

    scope = "sign_in"
    rate = "5/minute"


class RefreshTokenThrottle(AnonRateThrottle):
    """
    Throttle for token refresh endpoint.
    30 requests per minute per IP.
    """

    scope = "refresh_token"
    rate = "30/minute"


class VerifyTokenThrottle(AnonRateThrottle):
    """
    Throttle for token verify endpoint.
    60 requests per minute per IP.
    """

    scope = "verify_token"
    rate = "60/minute"


class SignOutThrottle(AnonRateThrottle):
    """
    Throttle for sign-out endpoint.
    10 requests per minute per IP.
    """

    scope = "sign_out"
    rate = "10/minute"
