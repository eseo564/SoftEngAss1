python
import json

#declaring INSTANCES (unique copies, not global variables) 
class Registration:
    __slots__ = ("registrationID", "eventID", "userID", "registeredAt")

    def __init__(
        self,
        registrationID: int,
        eventID: int,
        userID: int,
        registeredAt: str
    ):
        #isinstance checks if they are ints
        #len + .strip() checks date isn't empty or whitespace
        assert isinstance(registrationID, int), "Invalid registrationID"
        assert isinstance(eventID, int), "Invalid eventID"
        assert isinstance(userID, int), "Invalid userID"
        assert len(registeredAt.strip()) > 0, "Invalid registration date"

        self.registrationID = registrationID
        self.eventID = eventID
        self.userID = userID
        self.registeredAt = registeredAt

    #checks if you are comparing between Registration class to begin with
    def __eq__(self, other: "Registration"):
        if not isinstance(other, Registration):
            return NotImplemented

        return (
            self.eventID == other.eventID
            and self.userID == other.userID
        )

#reads registration data from a JSON file, converts to list of Registration objects
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


#1 check if an event ID exists
def eventExists(eventID: int, events: list) -> bool:
    for event in events:
        if event.eventID == eventID:
            return True
    return False


#2 check if a participant ID exists
def participantExists(userID: int, participants: list) -> bool:
    for participant in participants:
        if participant.userID == userID:
            return True
    return False


#3 check if a registration is allowed
def registrationChecker(
    eventID: int,
    registrations: list[Registration],
    events: list,
    currentTime: str
) -> bool:

    #finding the event
    event = None
    for e in events:
        if e.eventID == eventID:
            event = e
            break

    if event is None:
        return False

    #check the capacity
    count = 0
    for registration in registrations:
        if registration.eventID == eventID:
            count += 1

    if count >= event.capacity:
        return False

    #checking start time
    if event.startTime <= currentTime:
        return False

    return True


#4 check whether a registration ID already exists
def registrationExists(
    registrationID: int,
    registrations: list[Registration]
) -> bool:

    for registration in registrations:
        if registration.registrationID == registrationID:
            raise ValueError("Registration already exists!")

    return False


#5 check whether a time is in the future
def timeValid(time: str, currentTime: str) -> bool:
    return time > currentTime


#register a participant for an event
def registerEvent(
    eventID: int,
    userID: int,
    events: list,
    participants: list,
    registrations: list[Registration],
    currentTime: str
) -> Registration:

    #checking event and participant
    assert eventExists(eventID, events), "Event does not exist"
    assert participantExists(userID, participants), (
        "Participant does not exist"
    )

    #check whether the event has space & has not started
    assert registrationChecker(
        eventID, registrations, events, currentTime
    ), "Event is full or has already started"

    #check if this participant is already registered
    for registration in registrations:
        if (
            registration.eventID == eventID
            and registration.userID == userID
        ):
            raise ValueError("Participant already registered!")

    #generate a new registration ID
    registrationID = 1
    for registration in registrations:
        if registration.registrationID >= registrationID:
            registrationID = registration.registrationID + 1

    #creating the registration
    newRegistration = Registration(
        registrationID,
        eventID,
        userID,
        currentTime
    )

    registrations.append(newRegistration)
    return newRegistration


#canceling a participant's registration
def cancelRegistration(
    eventID: int,
    userID: int,
    events: list,
    participants: list,
    registrations: list[Registration]
) -> bool:

    assert eventExists(eventID, events), "Event does not exist"
    assert participantExists(userID, participants), (
        "Participant does not exist"
    )

    for registration in registrations:
        if (
            registration.eventID == eventID
            and registration.userID == userID
        ):
            registrations.remove(registration)
            return True

    raise ValueError("Registration does not exist")


#lists the participants registered for an event
def listEventParticipants(
    eventID: int,
    events: list,
    participants: list,
    registrations: list[Registration]
) -> list:

    assert eventExists(eventID, events), "Event does not exist"

    result = []

    for registration in registrations:
        if registration.eventID == eventID:
            for participant in participants:
                if participant.userID == registration.userID:
                    result.append(participant)
                    break

    return result
