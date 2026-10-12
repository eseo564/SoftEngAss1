import json


class Registration:
    __slots__ = ("registrationID", "eventID", "userID", "registeredAt")

    def __init__(
        self,
        registrationID: int,
        eventID: int,
        userID: int,
        registeredAt: str
    ):
        assert isinstance(registrationID, int), "Invalid registrationID"
        assert isinstance(eventID, int), "Invalid eventID"
        assert isinstance(userID, int), "Invalid userID"
        assert len(registeredAt.strip()) > 0, "Invalid registration date"

        self.registrationID = registrationID
        self.eventID = eventID
        self.userID = userID
        self.registeredAt = registeredAt

    def __eq__(self, other: "Registration"):
        if not isinstance(other, Registration):
            return NotImplemented

        return (
            self.eventID == other.eventID
            and self.userID == other.userID
        )


def loadDatabase():
    with open("RegistrationDatabase.json", "r") as database:
        registrations = json.load(database)

    return [
        Registration(
            registration["registrationID"],
            registration["eventID"],
            registration["userID"],
            registration["registeredAt"]
        )
        for registration in registrations
    ]


def registrationChecker(
    registrationID: int,
    registrations: list[Registration]
) -> bool:
    for registration in registrations:
        if registration.registrationID == registrationID:
            return True
    return False


def registrationExists(
    eventID: int,
    userID: int,
    registrations: list[Registration]
) -> bool:
    for registration in registrations:
        if (
            registration.eventID == eventID
            and registration.userID == userID
        ):
            return True
    return False


def registerEvent(
    eventID: int,
    userID: int,
    events: list,
    participants: list,
    registrations: list[Registration],
    currentTime: str
) -> Registration:
    # Check event exists.
    event = None
    for e in events:
        if e.eventID == eventID:
            event = e
            break

    assert event is not None, "Event does not exist"

    # Check participant exists.
    participant = None
    for p in participants:
        if p.userID == userID:
            participant = p
            break

    assert participant is not None, "Participant does not exist"

    # Check duplicate registration.
    assert not registrationExists(
        eventID, userID, registrations
    ), "Participant already registered"

    # Check event has not started.
    assert event.startTime > currentTime, "Event has already started"

    # Check capacity.
    count = 0
    for registration in registrations:
        if registration.eventID == eventID:
            count += 1

    assert count < event.capacity, "Event is full"

    # Create registration.
    registrationID = 1
    for registration in registrations:
        if registration.registrationID >= registrationID:
            registrationID = registration.registrationID + 1

    newRegistration = Registration(
        registrationID,
        eventID,
        userID,
        currentTime
    )

    registrations.append(newRegistration)
    return newRegistration


def cancelRegistration(
    eventID: int,
    userID: int,
    events: list,
    participants: list,
    registrations: list[Registration]
) -> bool:
    # Check event exists.
    assert any(e.eventID == eventID for e in events), (
        "Event does not exist"
    )

    # Check participant exists.
    assert any(p.userID == userID for p in participants), (
        "Participant does not exist"
    )

    # Find and remove registration.
    for registration in registrations:
        if (
            registration.eventID == eventID
            and registration.userID == userID
        ):
            registrations.remove(registration)
            return True

    raise ValueError("Registration does not exist")


def listEventParticipants(
    eventID: int,
    events: list,
    participants: list,
    registrations: list[Registration]
) -> list:
    # Check event exists.
    assert any(e.eventID == eventID for e in events), (
        "Event does not exist"
    )

    result = []

    # Find participants registered for this event.
    for registration in registrations:
        if registration.eventID == eventID:
            for participant in participants:
                if participant.userID == registration.userID:
                    result.append(participant)
                    break

    return result
