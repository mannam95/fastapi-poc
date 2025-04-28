# Domains Overview

This directory contains the business domains for the FastAPI application, organized in a domain-driven design (DDD) approach.

## Domain Structure

Each domain follows a similar structure:

```
domain_name/
├── domain_name_model.py            # SQLAlchemy models
├── domain_name_schema.py           # Pydantic schemas
├── domain_name_service.py          # Business logic
├── domain_name_router.py           # API endpoints
└── domain_name_dependencies.py     # Dependency injection
└── domain_name_repository.py       # Database operations (Not present as we are relying on SQLAlchemy ORM)
```

## Available Domains

- **department**: Department management
- **location**: Location management
- **process**: Business process definitions
- **resource**: Resource management
- **role**: User roles and permissions
- **user**: User management

## Adding a New Domain

1. Create a new directory for your domain
2. Add required files (model, schema, service, router, repository)
3. Register models in `app/models/__init__.py`
4. Register router in `app/api/api.py`

## Best Practices

- Keep the api router thin and delegate logic to the service layer
- Keep domain logic encapsulated within the service layer
- Use dependency injection for service and repository instances
- Use Pydantic schemas for data validation and serialization
- Use SQLAlchemy models for database interactions
- Use async functions for I/O-bound operations
- Define clear schemas for input validation and response serialization
- Follow consistent naming conventions
- Implement proper error handling and validation