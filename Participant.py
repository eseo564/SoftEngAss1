import json
import re

class Participant:
	__slots__ = ("userID", "name", "email")
	
	def __init__(
			self,
			userID: int,
			name: str,
			email: str
		):
		## Validate userID
		assert userID is not None, "userID cannot be null"
		assert isinstance(userID, int), "userID must be an integer"
		assert userID >= 0, "userID must be non-negative"

		## Validate name
		assert name is not None, "eame cannot be null"
		assert isinstance(name, str), "name must be a string"
		assert len(name.strip()) > 0, "Cannot have blank name"

		## Validate email
		assert email is not None, "email cannot be null"
		assert isinstance(email, str), "email must be a string"
		assert len(email.strip()) > 0, "Cannot have blank email"
		
		pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
		assert bool(re.match(pattern, email)), "Invalid email format"
		
		## Setup participant identifiers
		self.userID = userID
		self.name = name.strip()
		self.email = email.strip()

	def __eq__(self, other: "Participant"):
		if (not isinstance(other, Participant)):
			return NotImplemented
		return self.name == other.name and self.email == other.email
	
	def __lt__(self, other: "Participant") -> bool:
		if (not isinstance(other, Participant)):
			return NotImplemented

		return (self.userID, self.name, self.userID) < (other.userID, self.name, self.userID)

	def __hash__(self):
		return hash((self.name, self.email))

	def __str__(self):
		lines = [
			f"User ID: {self.userID}",
			f"Name:    {self.name}",
			f"Email:   {self.email}"
		]
		return '\n'.join(lines)

	def __repr__(self):
		return f"Participant({self.userID}, '{self.name}', '{self.email}')"



def loadParticipantDatabase() -> list[Participant]:
	with open("ParticipantDatabase.json", 'r') as database:
		people = json.load(database)

	db = [
		Participant(
			person["userID"],
			person["name"],
			person["email"]
		)
		for person in people
	]
	
	if (hasDuplicates(db)):
		db = removeDuplicates(db)
	db.sort()
	
	return db


def participantExists(participant: Participant, participants: list[Participant]) -> bool:
	for participant in participants:
		if (participant == participant):
			return True
	return False


def hasDuplicates(participants: list[Participant]) -> bool:
	hasDups = len(participants) != len(list(set(participants)))
	return hasDups


def removeDuplicates(participants: list[Participant]) -> list[Participant]:
	if (hasDuplicates(participants)):
		tmpParticipants = participants[:]
		tmpParticipants = list(set(tmpParticipants))
		tmpParticipants.sort()
		return tmpParticipants
	return participants




if (__name__ == "__main__"):
	db = loadParticipantDatabase()
	print(len(db))
	input()
