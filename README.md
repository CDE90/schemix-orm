# Schemix ORM

## Development Status

This project is currently in early development, and is not yet ready for production use.

## What is Schemix?

Schemix is a type-safe ORM for Python, designed to be easy to use and easy to learn, with SQL-like APIs. The goal is to provide a simple, intuitive, and powerful way to interact with databases that can be used in any Python project.

It is inspired heavily by [Drizzle ORM](https://github.com/drizzle-team/drizzle-orm), which is a TypeScript ORM with SQL-like query APIs.

## Why Schemix?

TODO...

## Current Features

TODO...

## Planned Features

TODO...

## Installation

TODO...

## Project Goals

### Overarching Goals

-   Create a simple SQL-like API for interacting with databases
-   Type-safety is a priority
-   Multiple supported database dialects
    -   SQLite
    -   PostgreSQL
    -   MySQL

### API Design Goals

SQL-like APIs for querying and manipulating data.

The below APIs are currently just proposed APIs, and are subject to change. Most notably, the decision on whether to use dictionaries or function arguments for selecting columns, or inserting values, etc. is still being decided.

```python
# Querying
results = await (
    db.select({"title": Post.title, "author_name": User.full_name})
    .from_(Post)
    .inner_join(User, Post.author_id == User.id)
    .where(Post.published == True)
    .order_by(Post.published_date)
    .limit(10)
    .execute()
)
results = await (
    db.select(title=Post.title, author_name=User.full_name)
    .from_(Post)
    .inner_join(User, Post.author_id == User.id)
    .where(Post.published == True)
    .order_by(Post.published_date)
    .limit(10)
    .execute()
)

# Inserting
await db.insert(Post).values({"title": "New Post", "content": "This is a new post"}).execute()
await db.insert(Post).values(title="New Post", content="This is a new post").execute()

# Updating
await db.update(Post).set({"title": "New Title"}).where(Post.id == 1).execute()
await db.update(Post).set(title="New Title").where(Post.id == 1).execute()

# Deleting
await db.delete(Post).where(Post.id == 1).execute()
```

From the above suggestions, the main aims are:

-   Ensure that the keywords used are consistent with SQL keywords
-   Ensure that the API flows in a similar order as SQL
-   Ensure that the API is clear and easy to understand
-   Ensure that the API is type-safe

### Schema Management and Design Goals

I want to create a simple way to define schemas for databases, in a way that is easy to understand, and similar to SQL. It is also important that the schemas are type-safe.

The proposed way to define a table is:

```python
class Post(BaseTable):
    __tablename__ = "posts"

    id: Integer("id").primary_key()
    title: Varchar("title", length=255).not_null()
    content: Text("content").not_null()
    author_id: Integer("author_id").references(User.id)
```

To then synchronise the schema with the database, I would like to use a "push" approach, where instead of generating migration files, the schema of the database is updated directly. Schema history will instead be retrievable from the version history of the project itself rather than the database.

### Database Support Goals

I want to support multiple database backends, with minimal changes to the codebase to transfer a project from one database to another.

Primarily, I would like to support SQLite, PostgreSQL, and MySQL, but the codebase should be written in a way that it is fairly easy to add support for other SQL-based databases.

## Contributing

Contributions are welcome!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
