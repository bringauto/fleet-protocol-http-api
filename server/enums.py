from aenum import UpperStrEnum


class MessageType(UpperStrEnum):
    STATUS = "STATUS"
    STATUS_ERROR = "STATUS_ERROR"
    COMMAND = "COMMAND"


class EncodingType(UpperStrEnum):
    BASE64 = "BASE64"
    JSON = "JSON"

