class AppException(Exception):

    def __init__(self, exception, message=None):
        super(AppException, self).__init__(exception)

        self.feedback = {
            "message": message
        }

