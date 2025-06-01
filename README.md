# Schemix ORM

## Development Status

This project is currently in early development, and is not yet ready for production use.

## What is Schemix?

Schemix is a type-safe ORM for Python, designed to be easy to use and easy to learn, with SQL-like APIs. The goal is to provide a simple, intuitive, and powerful way to interact with databases that can be used in any Python project.

It is inspired heavily by [Drizzle ORM](https://github.com/drizzle-team/drizzle-orm), which is a TypeScript ORM with SQL-like query APIs.

## Why Schemix?

TODO...

## Current Features

### ✅ Core Query Builder
- **SELECT queries** with type-safe column selection
- **WHERE clauses** with operator overloading (`==`, `!=`, `>`, `<`, etc.)
- **ORDER BY** with ascending/descending support
- **LIMIT** for result pagination
- **GROUP BY** with aggregation functions (`count()`, `avg()`, `sum()`, etc.)
- **JOIN operations** (INNER, LEFT, RIGHT, FULL OUTER)


### ✅ Type-Safe Schema Definition
- **Column types**: `Integer`, `Varchar`, `Text`, `Boolean`, `Date`, `Time`, `Timestamp`, `JSON`, `JSONB`
- **Column constraints**: `.primary_key()`, `.not_null()`, `.unique()`, `.default()`
- **Foreign key relationships**: `.references(Table.column, on_delete="cascade")`
- **Automatic table name generation** from class names

### ✅ Database Support
- **SQLite** with `aiosqlite` backend
- **PostgreSQL** with `asyncpg` backend
- **Connection helpers** for easy database setup
- **Foreign key constraint enforcement**

### ✅ Schema Generation
- **Automatic CREATE TABLE SQL generation** from table definitions
- **Foreign key constraint SQL generation**
- **Dialect-specific SQL** (SQLite vs PostgreSQL differences handled automatically)

### ✅ Developer Experience
- **Full type safety** with generics and TypeVars
- **MyPy integration** ready (plugin planned)
- **Operator overloading** for intuitive query building
- **Clear error messages** for configuration issues

## Planned Features

### 🚧 Query Operations
- **INSERT queries** with value insertion and conflict resolution
- **UPDATE queries** with conditional updates
- **DELETE queries** with WHERE conditions
- **Subqueries** and complex expressions
- **Transactions** and connection pooling

### 🚧 Advanced Schema Features  
- **Composite primary keys** and multi-column constraints
- **Indexes** for query optimization
- **CHECK constraints** for data validation
- **Custom column types** and domain types
- **Table inheritance** and polymorphic relationships

### 🚧 Schema Management
- **Push-based schema synchronization** (no migration files)
- **Schema diffing** and automatic updates
- **Data migration utilities** for schema changes
- **Schema versioning** through git history

### 🚧 Database Features
- **MySQL support** with `aiomysql` backend
- **Connection pooling** with automatic failover
- **Database introspection** and reverse engineering

### 🚧 Developer Tools
- **MyPy plugin** for enhanced type checking
- **CLI tools** for schema management
- **Query debugging** and performance analysis
- **IDE integration** with autocomplete support

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
class User(BaseTable):
    __tablename__ = "users"
    
    id = Integer("id").primary_key()
    name = Varchar("name", length=100).not_null()
    email = Varchar("email", length=100).not_null().unique()

class Post(BaseTable):
    __tablename__ = "posts"

    id = Integer("id").primary_key()
    title = Varchar("title", length=255).not_null()
    content = Text("content").not_null()
    author_id = Integer("author_id").references(User.id, on_delete="cascade")
```

To then synchronise the schema with the database, I would like to use a "push" approach, where instead of generating migration files, the schema of the database is updated directly. Schema history will instead be retrievable from the version history of the project itself rather than the database.

### Database Support Goals

I want to support multiple database backends, with minimal changes to the codebase to transfer a project from one database to another.

Primarily, I would like to support SQLite, PostgreSQL, and MySQL, but the codebase should be written in a way that it is fairly easy to add support for other SQL-based databases.

## Contributing

Contributions are welcome!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
