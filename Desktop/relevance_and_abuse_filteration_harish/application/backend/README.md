# Voice Up Backend

Flask backend for the Voice Up mobile application.

## Features

- User authentication with JWT tokens
- Post submission with parallel component processing
- Image upload and storage
- Notifications system
- SQLite database
- RESTful API

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python app.py
```

The server will start at `http://localhost:5000`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/profile` - Get user profile (requires auth)

### Posts
- `GET /api/posts` - Get all approved posts (dashboard)
- `GET /api/posts/user/<user_id>` - Get user's posts
- `POST /api/posts/submit` - Submit new post (requires auth)
- `GET /api/posts/<post_id>` - Get single post details
- `GET /api/posts/<post_id>/status` - Get processing status

### Notifications
- `GET /api/notifications/<user_id>` - Get user notifications
- `PUT /api/notifications/<notification_id>/read` - Mark as read
- `GET /api/notifications/unread-count/<user_id>` - Get unread count
- `PUT /api/notifications/mark-all-read/<user_id>` - Mark all as read

## Component Integration

The backend processes posts through 4 components in parallel:

1. **Component 1**: Relevance & Abuse Filtration (Harish's component)
2. **Component 2**: Placeholder (to be implemented)
3. **Component 3**: Placeholder (to be implemented)
4. **Component 4**: Placeholder (to be implemented)

All components must pass for a post to be approved.

## Database Schema

- **users**: User accounts
- **posts**: User submissions
- **notifications**: User notifications
- **component_results**: Component processing results
- **officer_replies**: Government officer responses

## File Structure

```
backend/
├── app.py                 # Main Flask application
├── config.py              # Configuration
├── models.py              # Database models
├── auth.py                # Authentication routes
├── posts.py               # Post management routes
├── notifications.py       # Notification routes
├── components.py          # Component integration
├── utils.py               # Helper functions
├── requirements.txt       # Dependencies
├── database.db           # SQLite database (auto-created)
└── uploads/              # Image storage (auto-created)
```

## Testing

Use Postman or curl to test the API endpoints.

Example: Register a user
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
    "mobile": "1234567890"
  }'
```
