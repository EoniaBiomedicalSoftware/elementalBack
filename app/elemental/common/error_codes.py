from enum import Enum


class ElementalErrorCode(Enum):
    """
    Standard error codes for the Elemental package.
    Each member contains an HTTP status code and a default message.
    """

    # --- 400 Bad Request ---
    INVALID_INPUT = (400, "The data provided is invalid.")
    MISSING_REQUIRED_FIELD = (400, "A required field in the payload is missing.")
    INVALID_FORMAT = (400, "The data has the right fields but the wrong format.")
    INVALID_QUERY_PARAMETER = (400, "There is an error in the URL query strings.")
    NOT_ALLOWED = (400, "The requested operation is not allowed.")

    # --- 401 Unauthorized ---
    UNAUTHORIZED = (401, "User is not authenticated.")
    AUTHENTICATION_ERROR = (401, "Authentication failed.")
    TOKEN_EXPIRED = (401, "The provided token has expired.")
    INVALID_TOKEN = (401, "The provided token is invalid.")
    TOKEN_REVOKED = (401, "The token has been revoked or is outdated.")
    INVALID_CREDENTIALS = (401, "Invalid email or password.")

    # --- 403 Forbidden ---
    FORBIDDEN = (403, "Access to this resource is forbidden.")
    PERMISSION_DENIED = (403, "You do not have the required permissions.")
    INSUFFICIENT_SCOPE = (403, "The token does not have the required scope.")
    ACCOUNT_DISABLED = (403, "Account is inactive or suspended.")
    ACCOUNT_NOT_VERIFIED = (403, "Account has not been verified yet.")

    # --- 404 Not Found ---
    NOT_FOUND = (404, "The requested resource was not found.")
    RESOURCE_NOT_FOUND = (404, "Resource not found.")
    USER_NOT_FOUND = (404, "The specified user does not exist.")
    ENDPOINT_NOT_FOUND = (404, "The requested endpoint does not exist.")

    # --- 409 Conflict ---
    CONFLICT = (409, "A conflict occurred with the current state of the resource.")
    DUPLICATE_ERROR = (409, "The resource already exists.")
    RESOURCE_ALREADY_EXISTS = (409, "This resource is already in use.")
    RESOURCE_STATE_CONFLICT = (409, "Operation cannot be performed due to resource state.")

    # --- 422 Unprocessable Entity ---
    VALIDATION_ERROR = (422, "Validation failed for the provided data.")
    BUSINESS_LOGIC_ERROR = (422, "The operation violates a business rule.")

    # --- 429 Too Many Requests ---
    RATE_LIMIT_ERROR = (429, "Too many requests. Please try again later.")
    TOO_MANY_REQUESTS = (429, "Rate limit exceeded.")

    # --- 500 Internal Server Error ---
    INTERNAL_SERVER_ERROR = (500, "An unexpected internal server error occurred.")

    # --- 502 Bad Gateway ---
    EXTERNAL_SERVICE_ERROR = (502, "An error occurred while communicating with an external service.")
    OAUTH_ERROR = (502, "The OAuth provider returned an error.")
    BAD_GATEWAY = (502, "Upstream server returned an invalid response.")

    # --- 503 Service Unavailable ---
    SERVICE_UNAVAILABLE = (503, "The service is currently unavailable.")
    DATABASE_CONNECTION_FAILED = (503, "Could not connect to the database.")
    EXTERNAL_SERVICE_UNAVAILABLE = (503, "Third-party service is down.")

    # --- 504 Gateway Timeout ---
    GATEWAY_TIMEOUT = (504, "The upstream server took too long to respond.")

    def __init__(self, http_code: int, default_message: str):
        """
        Initializes an instance of a class that represents an HTTP response code and its associated default message.

        Attributes:
        http_code (int): The HTTP status code.
        default_message (str): The default message describing the HTTP status.
        """
        self.http_code = http_code
        self.default_message = default_message

    @classmethod
    def to_dict(cls):
        """
        Returns a dictionary mapping error names to their HTTP status codes.
        Example: {"UNAUTHORIZED": 401, "NOT_FOUND": 404, ...}
        """
        return {item.name: item.http_code for item in cls}