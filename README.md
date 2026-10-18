# Campus Club API
A REST API for campus clubs offering activities such as pottery workshops, board game nights, and photography walks! The service manages events and lets existing participants register or cancel bookings.

## Steps to build:
Set all this up on your virtual machine, we used Google Cloud
1) **Environment Setup**
   - Create a ```.env``` file in the root directory
   - Copy the ```.env.example``` as ```.env``` (```cp .env.example .env```)
   - Open ```.env``` and fill in YOUR specific credentials
3) Install Dependencies
4) Database Initialization
5) Running Application Locally
   - Run ```python main.py``` on the command line
### Known limitations:

## Command environments and working directories:

## How to run tests separately 

## API contract:
### Participant class
| **Method** | **URL** | **Purpose** |
| :--- | :--- | :--- |
| `GET` | `/api/v1/participants` | Returns all participants |
| `GET` | `/api/v1/participants/<participantID>` | Returns details of a specific participant |
| `POST` | `/api/v1/participants` | Creates a new participant  |
| `PATCH` | `/api/v1/participants/<participantID>` | Updates an existing participant |
| `DELETE` | `/api/v1/participants/<participantID>` | Deletes an existing participant |

### Registration class
| **Method** | **URL** | **Purpose** |
| :--- | :--- | :--- |
| `GET` | `/api/v1/registrations` | Returns all registrations |
| `GET` | `/api/v1/registrations/<registrationID>` | Returns details of a specific registration |
| `POST` | `/api/v1/registrations` | Registers a participant for an event |
| `DELETE` | `/api/v1/registrations/<registrationID>` | Cancels an existing registration |

### Event class
| **Method** | **URL** | **Purpose** |
| :--- | :--- | :--- |
| `GET` | `/api/v1/events` | Returns all events |
| `GET` | `/api/v1/events/<eventID>` | Returns details of a specific event |
| `POST` | `/api/v1/events` | Creates a new event |
| `PATCH` | `/api/v1/events/<eventID>` | Updates an existing event |
| `DELETE` | `/api/v1/events/<eventID>` | Deletes an existing event |

