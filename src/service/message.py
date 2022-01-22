import shortuuid


class Message:
    def __init__(self, id):
        if id is None:
            self._id = shortuuid.uuid()

    @property
    def id(self):
        return self._id


class ServiceRequest(Message):
    def __init__(self, id):
        super().__init__(id)


class ServiceError(Message):
    def __init__(self, id, code: int, message: str=None, details: str=None):
        super().__init__(id)
        self.code = code
        self.message = message
        self.details = details


class ServiceResponse(Message):
    def __init__(self, id, ret_data):
        super().__init__(id)
        self.ret_data = ret_data
