class Status:
    def __init__(self, code=500, message="unknown error"):
        self.code = code
        self.message = message

    def __str__(self):
        return f"code={self.code} message={self.message}"

    def get(self):
        return {"code": self.code, "message": self.message}
