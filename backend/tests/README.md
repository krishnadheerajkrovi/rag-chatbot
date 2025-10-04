# Testing Guide

## Running Tests

### Install test dependencies
```bash
pip install pytest pytest-cov httpx
```

### Run all tests
```bash
pytest
```

### Run with coverage
```bash
pytest --cov=app --cov-report=html
```

### Run specific test file
```bash
pytest tests/test_auth.py
pytest tests/test_folders.py
pytest tests/test_chat.py
```

### Run with verbose output
```bash
pytest -v
```

## Test Structure

```
tests/
├── __init__.py
├── test_auth.py       # Authentication tests
├── test_folders.py    # Folder management tests
├── test_chat.py       # Chat and query tests
└── README.md          # This file
```

## Test Coverage

- ✅ User registration
- ✅ User login
- ✅ Protected endpoints
- ✅ Folder CRUD operations
- ✅ Folder archive/unarchive
- ✅ Chat session management
- ✅ Chat queries
- ✅ Folder-scoped queries

## CI/CD Integration

Add to `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pip install pytest pytest-cov
      - run: pytest --cov=app
```

## Manual Testing Checklist

### Authentication
- [ ] Register new user
- [ ] Login with valid credentials
- [ ] Login with invalid credentials
- [ ] Access protected endpoint without token
- [ ] Logout and verify session cleared

### Folders
- [ ] Create folder
- [ ] List folders
- [ ] Update folder
- [ ] Archive folder
- [ ] View archived folders
- [ ] Unarchive folder
- [ ] Delete folder permanently

### Chats
- [ ] Create chat in folder
- [ ] Create chat without folder
- [ ] List chats
- [ ] Switch between chats
- [ ] Chat history persists
- [ ] Delete chat

### Documents
- [ ] Upload document to folder
- [ ] Upload document without folder
- [ ] List documents
- [ ] Delete document
- [ ] Query uses folder-scoped documents

### RAG Queries
- [ ] Query without documents
- [ ] Query with documents
- [ ] Folder-scoped query
- [ ] Global query (no folder)
- [ ] Chat history maintained
- [ ] Source documents returned
