# Working with Async SQLAlchemy

## Using Database Sessions

```python
from app.core.database import DBSessionDep

@router.get("/items")
async def read_items(session: DBSessionDep):
    result = await session.execute(select(Item))
    items = result.scalars().all()
    return items
```

## Common Operations

### Get Item by ID

```python
item = await session.get(Item, item_id)
```

### Query Items

```python
result = await session.execute(select(Item).where(Item.name == "test"))
items = result.scalars().all()
```

### Create Item

```python
item = Item(name="New Item")
session.add(item)
await session.commit()
await session.refresh(item)
```

### Update Item

```python
item = await session.get(Item, item_id)
item.name = "Updated Name"
await session.commit()
```

### Delete Item

```python
item = await session.get(Item, item_id)
await session.delete(item)
await session.commit()
```

For more detailed documentation, refer to the API docs at http://localhost:8000/docs when the application is running.
