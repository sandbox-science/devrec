from .session import Session


class Logger:
    def __init__(self, session: Session):
        self.session: Session = session

    def note(self, message: str):
        """
        Log a note.

        :param message: The note the user wants to log.
        :type message str:
        """
        self.session.add_event("note", message)
        self.session.save()
