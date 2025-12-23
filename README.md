# Team Nexus - Fertility Tracking API

## Project Overview

Team Nexus is a comprehensive fertility tracking and cycle monitoring platform designed to empower users with personalized insights into their menstrual health. Built with FastAPI and PostgreSQL, this backend service provides intelligent cycle predictions, ovulation tracking, and multilingual support to help users understand their fertility patterns and make informed decisions about their reproductive health.

The platform features:
- 🔐 Secure user authentication with OTP verification
- 📅 Advanced cycle tracking and predictions
- 🧠 AI-powered fertility insights
- 🌍 Multilingual support (English, Yoruba, Igbo, Hausa)
- 📊 Comprehensive symptom logging and analysis

---

## Base URL

**Development:**
```
http://localhost:8000
```

**Production:**
```
https://your-production-domain.com
```

All API endpoints are prefixed with the base URL.

---

## Global Headers

All API requests (except authentication) must include the following headers:

| Header | Value | Description |
|--------|-------|-------------|
| `Content-Type` | `application/json` | Specifies the request body format |
| `Accept` | `application/json` | Specifies the expected response format |
| `Authorization` | `Bearer <token>` | JWT token obtained from authentication |

**Example:**
```http
Content-Type: application/json
Accept: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Security & CORS

### CORS Configuration

The API implements Cross-Origin Resource Sharing (CORS) to allow controlled access from approved frontend applications.

**Allowed Origins:**
- `http://localhost:3000` - Local development
- `http://127.0.0.1:3000` - Local development (alternative)
- `https://teamnexuss.netlify.app/` - Production frontend

### Preflight Requests

The server handles OPTIONS preflight requests for cross-origin requests. All HTTP methods (GET, POST, PUT, DELETE) are allowed, and credentials (cookies, authorization headers) are supported.

**CORS Settings:**
- **Allow Credentials:** Yes
- **Allowed Methods:** All (`GET`, `POST`, `PUT`, `DELETE`, `PATCH`, `OPTIONS`)
- **Allowed Headers:** All headers are permitted

### Authentication

The API uses JWT (JSON Web Token) bearer authentication. Tokens are obtained through the login endpoint and must be included in the `Authorization` header for protected endpoints.

**Token Expiration:** 20 minutes

---

## API Endpoints

### User Authentication

#### Login

Authenticate a user and receive an access token.

**Endpoint:** `POST /auth/token`

**Description:** Authenticates a user with username and password, returning a JWT access token for subsequent API requests.

**Request Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `username` | string | Yes | User's username or email |
| `password` | string | Yes | User's password |

**Request Body:**
```json
{
  "username": "john_doe",
  "password": "SecureP@ss123"
}
```

**Note:** This endpoint uses `application/x-www-form-urlencoded` format (OAuth2 standard).

<details>
<summary>Success Response (200 OK)</summary>

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huX2RvZSIsImlkIjoxLCJyb2xlIjoidXNlciIsImV4cCI6MTcwMzM0NTY3OH0.xyz123abc456",
  "token_type": "bearer"
}
```
</details>

---

#### Register (Send OTP)

Initiate user registration by sending an OTP verification code.

**Endpoint:** `POST /auth/send-otp`

**Description:** Sends a one-time password to the user's email or phone for account verification.

**Request Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string (email) | Yes | User's email address |
| `username` | string | Yes | Desired username (3-40 characters) |
| `first_name` | string | Yes | User's first name |
| `last_name` | string | Yes | User's last name |
| `password` | string | Yes | Password (minimum 8 characters) |
| `role` | string | Yes | User role (e.g., "user") |
| `phone_number` | string | Yes | User's phone number |
| `language_preference` | string | No | Preferred language (en, yo, ig, ha) |

**Request Body:**
```json
{
  "email": "jane.smith@example.com",
  "username": "jane_smith",
  "first_name": "Jane",
  "last_name": "Smith",
  "password": "SecureP@ss123",
  "role": "user",
  "phone_number": "+2348012345678",
  "language_preference": "en"
}
```

<details>
<summary>Success Response (200 OK)</summary>

```json
{
  "message": "OTP sent successfully",
  "verification_id": "a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8"
}
```
</details>

---

#### Verify OTP

Complete user registration by verifying the OTP code.

**Endpoint:** `POST /auth/verify-otp`

**Description:** Verifies the OTP code and creates the user account.

**Request Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `verification_id` | string | Yes | Verification ID from send-otp response |
| `otp_code` | string | Yes | 6-digit OTP code received |

**Request Body:**
```json
{
  "verification_id": "a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8",
  "otp_code": "123456"
}
```

<details>
<summary>Success Response (201 Created)</summary>

```json
{
  "message": "User created successfully",
  "user_id": 42
}
```
</details>

---

### Calendar Logging (Cycle Tracking)

#### Log Cycle Data

Record menstrual cycle information including dates, symptoms, and cycle characteristics.

**Endpoint:** `POST /cycle/cycles`

**Description:** Logs cycle data for a specific date range with symptom markers, enabling tracking of menstrual patterns and generating fertility predictions.

**Request Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `last_period_date` | string (date) | Yes | Start date of last period (YYYY-MM-DD) |
| `cycle_length` | integer | Yes | Length of menstrual cycle in days (21-32) |
| `period_length` | integer | Yes | Duration of period in days (2-10) |
| `symptoms` | array[string] | No | List of symptoms experienced |

**Available Symptoms:**
- `headache`
- `nausea`
- `cramps`
- `fatigue`
- `breast_tenderness`
- `acne`

**Request Body:**
```json
{
  "last_period_date": "2025-01-15",
  "cycle_length": 28,
  "period_length": 5,
  "symptoms": ["cramps", "fatigue", "breast_tenderness"]
}
```

<details>
<summary>Success Response (200 OK)</summary>

```json
{
  "period_start": "2025-01-15",
  "period_end": "2025-01-19",
  "period_length": 5,
  "next_period": "2025-02-12",
  "ovulation_day": "2025-01-29",
  "fertile_window": ["2025-01-24", "2025-02-03"],
  "fertility_score": 85
}
```
</details>

---

#### Get Cycle History

Retrieve logged cycle data for the authenticated user.

**Endpoint:** `GET /cycle/cycles`

**Description:** Fetches all cycle records for the user, showing historical tracking data.

**Request Parameters:**

None (uses authenticated user from token)

**Request Headers:**
```http
Authorization: Bearer <your_token>
```

<details>
<summary>Success Response (200 OK)</summary>

```json
[
  {
    "Cycle_id": 1,
    "last_period_date": "2025-01-15",
    "Cycle_length": 28,
    "Period_length": 5
  },
  {
    "Cycle_id": 2,
    "last_period_date": "2024-12-18",
    "Cycle_length": 29,
    "Period_length": 4
  }
]
```
</details>

---

### Cycle Insights

#### Generate Insights

Generate personalized fertility insights and predictions based on cycle data.

**Endpoint:** `POST /insights/insights`

**Description:** Provides ovulation predictions, fertile window summaries, and personalized insights in the user's preferred language based on their cycle data.

**Request Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `cycle_length` | integer | Yes | Length of menstrual cycle in days |
| `last_period_date` | string (date) | Yes | Start date of last period (YYYY-MM-DD) |
| `period_length` | integer | Yes | Duration of period in days |
| `symptoms` | array[string] | No | List of symptoms experienced |

**Request Body:**
```json
{
  "cycle_length": 28,
  "last_period_date": "2025-01-15",
  "period_length": 5,
  "symptoms": ["cramps", "fatigue"]
}
```

<details>
<summary>Success Response (200 OK)</summary>

```json
{
  "predictions": {
    "period_start": "2025-01-15",
    "period_end": "2025-01-19",
    "period_length": 5,
    "next_period": "2025-02-12",
    "ovulation_day": "2025-01-29",
    "fertile_window": ["2025-01-24", "2025-02-03"],
    "fertility_score": 85
  },
  "insight": "You are currently in your follicular phase. Your fertility is increasing as you approach ovulation on Jan 29. This is an optimal time for conception if you're trying to conceive."
}
```
</details>

---

#### Get User Insights

Retrieve stored insights for the authenticated user.

**Endpoint:** `GET /insights/insights`

**Description:** Fetches previously generated insights and fertility predictions for the user.

**Request Parameters:**

None (uses authenticated user from token)

**Request Headers:**
```http
Authorization: Bearer <your_token>
```

<details>
<summary>Success Response (200 OK)</summary>

```json
[
  {
    "next_period": "2025-02-12",
    "ovulation_day": "2025-01-29",
    "fertile_period_start": "2025-01-24",
    "fertile_period_end": "2025-02-03",
    "symptoms": ["cramps", "fatigue"]
  }
]
```
</details>

---

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate user!"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Something went wrong: [error message]"
}
```

---

## Development Setup

### Prerequisites
- Python 3.11+
- PostgreSQL
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/teamnexusapp/Team-nexus.git
cd Team-nexus
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Create .env file with required variables
DATABASE_URL=postgresql://user:password@localhost/teamnexus
SECRET_KEY=your-secret-key
```

4. Run database migrations:
```bash
alembic upgrade head
```

5. Start the development server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

---

## API Documentation

Interactive API documentation is available at:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

---

## Technologies Used

- **Framework:** FastAPI 0.121.3
- **Database:** PostgreSQL with SQLAlchemy 2.0.44
- **Authentication:** JWT (PyJWT 2.10.1)
- **Password Hashing:** bcrypt 4.0.1
- **Migrations:** Alembic 1.17.2
- **Email Service:** SendGrid 6.12.5
- **AI/ML:** Cohere 4.57
- **Translations:** deep-translator 1.11.4

---

## License

This project is proprietary software developed by Team Nexus.

---

## Support

For issues, questions, or support, please contact the development team or create an issue in the repository.
