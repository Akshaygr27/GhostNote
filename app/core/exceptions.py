class MessageNotFoundException(Exception):

    def __init__(self, message_id: str):

        self.message_id = message_id

        super().__init__(
            f"Message with ID {message_id} not found"
        )