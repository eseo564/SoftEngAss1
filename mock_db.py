
# mock_db.py

EVENTS = [
    {
        "id": 1,
        "name": "Game Night",
        "date": "10/20/2026",
        "time": "18:00",
        "capacity": 20,
        "location": "Community Hall"
    },
    {
        "id": 2,
        "name": "Coding Workshop",
        "date": "10/22/2026",
        "time": "14:00",
        "capacity": 15,
        "location": "Library"
    }
]

NEXT_ID = 3


def add_event(event):
    """Add an event to the shared mock database."""
    global NEXT_ID

    new_event = {
        **event,
        "id": NEXT_ID
    }

    EVENTS.append(new_event)
    NEXT_ID += 1
    return new_event


class MockCursor:
    def __init__(self):
        self.results = []
        self.last_result = None

    def execute(self, query, params=None):
        query_upper = " ".join(query.upper().split())
        params = params or ()

        if query_upper.startswith("SELECT") and "FROM EVENTS" in query_upper:
            event_id = params[0] if params else None

            if "WHERE ID = %S" in query_upper:
                self.results = [
                    dict(event) for event in EVENTS
                    if event["id"] == event_id
                ]
            else:
                self.results = [dict(event) for event in EVENTS]

        elif query_upper.startswith("DELETE FROM EVENTS"):
            event_id = params[0] if params else None

            EVENTS[:] = [
                event for event in EVENTS
                if event["id"] != event_id
            ]

            self.results = []

        else:
            raise NotImplementedError(
                f"Mock SQL does not support this query: {query}"
            )

        self.last_result = (
            dict(self.results[0]) if self.results else None
        )

    def fetchone(self):
        return self.last_result

    def fetchall(self):
        return self.results

    def close(self):
        pass


class MockConnection:
    def cursor(self, dictionary=True):
        return MockCursor()

    def commit(self):
        pass

    def close(self):
        pass


def get_db():
    return MockConnection()
