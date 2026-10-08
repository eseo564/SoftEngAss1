import json
import re

class Participant:
	__slots__ = ("userID", "name", "email")
	
	def __init__(self, userID: int, name: str, email: str):
		assert isinstance(userID, int), "Invalid userID"
		assert len(name.strip()) > 0, "Cannot have blank name"

		## Validate email
		assert len(email.strip()) > 0, "Cannot have blank email"
		
		pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
		assert bool(re.match(pattern, email)), "Invalid email format"
		
		## Setup participant identifiers
		self.userID = userID
		self.name = name
		self.email = email

	def __eq__(self, other: "Participant"):
		if (not isinstance(other, Participant)):
			return NotImplemented
		return self.name == other.name and self.email == other.email
		#return self.userID == other.userID and self.name == other.name and self.email == other.email
	
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

	
	def placeholderFunction(self):
		## Use me if you need me
		pass


def loadDatabase():
	with open("ParticipantDatabase.json", 'r') as database:
		people = json.load(database)

	return [
		Participant(person["userID"], person["name"], person["email"])
		for person in people
	]

def participantExists(name: str, email: str, participants: list[Participant]) -> bool:
	for participant in participants:
		if (name == participant.name and email == participants.email):
			return True
	return False

def hasDuplicates(participants: list[Participant]):
	hasDups = len(participants) != len(list(set(participants)))
	return hasDups

def removeDuplicates(participants: list[Participant]) -> list[Participant]:
	if (hasDuplicates(participants)):
		tmpParticipants = participants[:]
		tmpParticipants = list(set(tmpParticipants))
		tmpParticipants.sort()
		return tmpParticipants
	return participants


db = loadDatabase()
print(hasDuplicates(db))
uniqueDB = removeDuplicates(db)
for p in uniqueDB:
	print(p, end="\n\n")
print()
input()
