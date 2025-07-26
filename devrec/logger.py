from .session import Session

class Logger:
    def __init__(self, session: Session):
        self.session = session

    def note(self, message: str):
        self.session.add_event("note", message)
        self.session.save()