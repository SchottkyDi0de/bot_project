from pydantic import BaseModel


class ErrorResponse(BaseModel):
    error: str
    message: str
    code: int
    traceback: str | None = None
    
    def add_traceback(self, traceback: str):
        self.traceback = traceback