# Campus Club API

A REST API for campus clubs offering activities such as pottery workshops, board game nights, and photography walks! The service manages events and lets existing participants register for or cancel bookings.

## Steps to Configure and Build

The API was developed and deployed using Google Cloud Compute Engine. The following instructions explain how to set up and run the project from a fresh clone.

### 1. Environment Setup

- Clone the repository:
  ```bash
  git clone YOUR_GITHUB_REPOSITORY_URL
  ```
- Navigate to the project directory:
  ```bash
  cd YOUR_PROJECT_DIRECTORY
  ```
- Create a virtual environment:
  ```bash
  python3 -m venv .venv
  ```
- Activate the virtual environment:
  ```bash
  source .venv/bin/activate
  ```
- Create a `.env` file in the root directory by copying `.env.example`:
  ```bash
  cp .env.example .env
  ```
- Open `.env` and fill in the required environment variables and credentials.
- Install the required dependencies:
  ```bash
  pip install -r requirements.txt
  ```

**Note:** Do not commit actual passwords, API keys, or other sensitive credentials to the repository.

### 2. Database Initialization

- Our version of the application uses a database hosted on Google Cloud.
- Configure the database connection using the provided environment variables.
- Ensure the database schema and required tables are created before running the application.
- If the database is already populated with the required fictional participant and event records, no additional seeding is necessary.

### 3. Command Environments and Working Directories

- **Command environment:** Activate the Python virtual environment before running the application or tests:
  ```bash
  source .venv/bin/activate
  ```
- **Working directory:** Run commands from the project root directory, where `main.py`, `requirements.txt`, and the `tests/` directory are located.
- If you are in a different directory, navigate to the project root:
  ```bash
  cd YOUR_PROJECT_DIRECTORY
  ```
- **Main application file:** `main.py` is the main entry point for running the API locally.

### 4. Running the API Locally

- From the project root directory, start the Flask application:
  ```bash
  python main.py
  ```
- If the application is configured to use port 5000, access it at:
  ```text
  http://localhost:5000
  ```
- Test the implemented endpoints using `curl`, a browser, or an API testing tool such as Postman.

Example requests:

```bash
curl http://localhost:5000/api/v1/events
```

```bash
curl http://localhost:5000/api/v1/events/1
```

Use the actual endpoints implemented in the project.

### 5. Deployment on Google Cloud Compute Engine

The API is deployed using Google Cloud Compute Engine, which runs the application on a virtual machine.

- **Cloud platform:** Google Cloud
- **Compute service:** Compute Engine
- **Deployed API URL:** YOUR_GOOGLE_CLOUD_API_URL (external)

Replace the URL placeholder with the public URL or IP address of the deployed API.

To test the deployed API, replace the local base URL with the deployed URL:

```bash
curl YOUR_GOOGLE_CLOUD_API_URL/api/v1/events
```

The Compute Engine virtual machine must be running, the Flask application must be started, and the required network and firewall settings must allow access to the API.

For deployment or maintenance, connect to the virtual machine using the configured Google Cloud SSH access and follow the project's environment setup and application startup instructions.

### 6. Participant IDs

Participants are fictional records preloaded using a seed script. Creating new participants through the API is not supported.

Use the preloaded participant IDs when testing endpoints that require a participant ID. (*Refer to the seed data for the complete list of available participants.*)

Example database format for Participant class: *the userID will be indexed by 1* 
| **userID** | **name** | **email** |
| :--- | :--- | :--- |
| 1 | Jane Doe | janedoe@email.com |

### 7. Running Tests

All tests use Flask to send requests to the API and verify the expected responses.

**Command environment:** Activated Python virtual environment.

**Working directory:** Project root directory, where `main.py` and the `tests/` folder are located.

### Running Integration Tests vs. Isolated Tests

**Isolated tests** verify individual components or functions independently, often using mocks to avoid relying on external components such as a database.
- Run the tests for each class separately:

```bash
python -m pytest -v tests/events_test.py
python -m pytest -v tests/registration_test.py
python -m pytest -v tests/participant_test.py
```

**Integration tests** verify that multiple components work together correctly, such as API endpoints interacting with a database or mock database.

Run all tests:

```bash
python -m pytest -v tests/
```

## Known Limitations
- No idempotency key, so in the event that a duplicate request occurs, the server will fulfill that secondary request.
  - Rejecting a duplicate registration is handled within the code. 
- Participants are fictional records preloaded using a seed script. The API does not support creating new participants.
- Participant search, filtering, and booking history are not supported.
- The API does not include authentication or participant account management.
- Participant information is limited to the fields provided in the existing dataset.
- Events do not support waitlisting when capacity is reached.
- The API only supports the endpoints and functionality implemented in the project.
  
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

