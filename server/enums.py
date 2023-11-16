from aenum import IntEnum


class MessageType(IntEnum):
    STATUS_TYPE = 0
    COMMAND_TYPE = 1


class EncodingType(IntEnum):
    BASE64 = 0
    JSON = 1

 