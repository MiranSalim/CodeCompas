# API Documentation

## Authentication Endpoints

### POST `/api/login`

**Body**:

```json
{
  "email": "admin@example.com",
  "password": "secret"
}
```

**Success Response (200 OK)**:

* Zet een `HttpOnly` cookie met JWT van Supabase
* Body:

```json
{ "ok": true }
```

**Error Responses**:

* `400 Bad Request` → als email of password ontbreekt
* `401 Unauthorized` → verkeerde credentials
* `403 Forbidden` → gebruiker bestaat niet of is geen admin

---

### GET `/api/me`

**Description**: Retourneert profielinfo van ingelogde gebruiker.
Leest JWT uit HttpOnly cookie.

**Success Response (200 OK)**:

```json
{
  "id": 1,
  "email": "admin@example.com",
  "name": "Admin User",
  "role": "ADMIN"
}
```

**Error Responses**:

* `401 Unauthorized` → niet ingelogd of ongeldig token
* `403 Forbidden` → profiel niet gevonden

---

### POST `/api/logout`

**Description**: Verwijdert de sessiecookie.

**Success Response (200 OK)**:

```json
{ "ok": true }
```

---

## Example cURL Commands

### Login

```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"secret"}' \
  -c cookies.txt
```

### Me

```bash
curl http://localhost:5000/api/me \
  -b cookies.txt
```

### Logout

```bash
curl -X POST http://localhost:5000/api/logout \
  -b cookies.txt
```

---

## Acceptance Criteria

* [x] **ORM werkt** → tabellen (`Profile`, `Topic`, `Subtopic`) worden aangemaakt bij startup.
* [x] **/api/login zet HttpOnly cookie** → cookie bevat Supabase JWT, `HttpOnly`, `SameSite=Strict`, `Secure` (indien ingesteld).
* [x] **Alleen admins kunnen inloggen** → role in `Profile` moet `ADMIN` zijn, anders `403 Forbidden`.
* [x] **/api/me retourneert profielinfo** → gebruiker moet ingelogd zijn, anders `401/403`.
* [x] **/api/logout wist cookie** → session cookie wordt verwijderd.
ut