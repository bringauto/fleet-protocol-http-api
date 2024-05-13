from aenum import UpperStrEnum


class MessageType(UpperStrEnum):
    STATUS = "STATUS"
    COMMAND = "COMMAND"


class EncodingType(UpperStrEnum):
    BASE64 = "BASE64"
    JSON = "JSON"

