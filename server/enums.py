from aenum import UpperStrEnum


class MessageType(UpperStrEnum):
    STATUS_TYPE = "STATUS"
    COMMAND_TYPE = "COMMAND"


class EncodingType(UpperStrEnum):
    BASE64 = "BASE64"
    JSON = "JSON"

    