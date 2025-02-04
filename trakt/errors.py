# -*- coding: utf-8 -*-
"""All Trakt related errors that are worth processing. Note that 412 response
codes are ignored because the only requests that this library sends out are
guaranteed to have the application/json MIME type set.
"""

__author__ = 'Jon Nappi'
__all__ = [
    # Base Exception
    'TraktException',

    # Errors for use by PyTrakt
    'BadResponseException',
    'OAuthRefreshException',

    # Exceptions by HTTP status code
    # https://trakt.docs.apiary.io/#introduction/status-codes
    'AccountLimitExceeded',
    'BadRequestException',
    'OAuthException',
    'ForbiddenException',
    'NotFoundException',
    'MethodNotAllowedException',
    'ConflictException',
    'ProcessException',
    'LockedUserAccountException',
    'RateLimitException',
    'TraktInternalException',
    'TraktBadGateway',
    'TraktUnavailable',
]


class TraktException(Exception):
    """Base Exception type for trakt module"""

    http_code = message = None

    def __init__(self, response=None):
        self.response = response

    def __str__(self):
        return self.message


class BadResponseException(TraktException):
    """TraktException type to be raised when json could not be decoded"""

    http_code = -1
    message = "Bad Response - Response could not be parsed"

    def __init__(self, response=None, details=None):
        super().__init__(response)
        self.details = details


class BadRequestException(TraktException):
    """TraktException type to be raised when a 400 return code is received"""

    http_code = 400
    message = "Bad Request - request couldn't be parsed"


class OAuthException(TraktException):
    """TraktException type to be raised when a 401 return code is received"""

    http_code = 401
    message = 'Unauthorized - OAuth must be provided'


class OAuthRefreshException(OAuthException):
    def __init__(self, response=None):
        super().__init__(response)
        self.data = self.response.json()

    @property
    def error(self):
        return self.data["error"]

    @property
    def error_description(self):
        return self.data["error_description"]


class ForbiddenException(TraktException):
    """TraktException type to be raised when a 403 return code is received"""

    http_code = 403
    message = 'Forbidden - invalid API key or unapproved app'


class NotFoundException(TraktException):
    """TraktException type to be raised when a 404 return code is received"""

    http_code = 404
    message = 'Not Found - method exists, but no record found'


class MethodNotAllowedException(TraktException):
    """TraktException type to be raised when a 405 return code is received"""

    http_code = 405
    message = 'Method Not Found - method doesn\'t exist'


class ConflictException(TraktException):
    """TraktException type to be raised when a 409 return code is received"""

    http_code = 409
    message = 'Conflict - resource already created'


class ProcessException(TraktException):
    """TraktException type to be raised when a 422 return code is received"""

    http_code = 422
    message = 'Unprocessable Entity - validation errors'


class LockedUserAccountException(TraktException):
    """TraktException type to be raised when a 423 return code is received"""

    http_code = 423
    message = 'Locked User Account - have the user contact support'


class RateLimitException(TraktException):
    """TraktException type to be raised when a 429 return code is received"""

    http_code = 429
    message = 'Rate Limit Exceeded'

    @property
    def retry_after(self):
        return int(self.response.headers.get("retry-after", 1))

    @property
    def details(self):
        from json import JSONDecodeError, loads

        try:
            return loads(self.response.headers.get("x-ratelimit", ""))
        except JSONDecodeError:
            return None


class AccountLimitExceeded(RateLimitException):
    """TraktException type to be raised when a 420 return code is received"""
    http_code = 420
    message = 'Account Limit Exceeded - list count, item count, etc'

    @property
    def account_limit(self):
        """Get the account limit details from response headers.

        Returns:
            str|None: The value of x-account-limit header or None if not present
        """
        return self.response.headers.get("x-account-limit", None)


class TraktInternalException(TraktException):
    """TraktException type to be raised when a 500 error is raised"""

    http_code = 500
    message = 'Internal Server Error'

    @property
    def error_message(self):
        return self.response.headers.get("x-error-message", None)


class TraktBadGateway(TraktException):
    """TraktException type to be raised when a 502 error is raised"""

    http_code = 502
    message = 'Trakt Unavailable - Bad Gateway'


class TraktUnavailable(TraktException):
    """TraktException type to be raised when a 503 error is raised"""

    http_code = 503
    message = 'Trakt Unavailable - server overloaded'
