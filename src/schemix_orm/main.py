import asyncio
import json
import logging

import aiosqlite

from schemix.database import Database
from schemix.dialects import Dialect
from schemix.helpers import create_sqlite_connection
from schemix.logging import configure_logging
from schemix.schema import generate_create_table_sql
from schemix.sqlite import JSON, Integer, Text
from schemix.table import BaseTable


class Users(BaseTable):
    """Example table class for Users."""

    __tablename__ = "users"

    id = Integer("id").primary_key()
    name = Text("name").not_null()
    email = Text("email").not_null().unique()
    age = Integer("age").not_null()
    is_active = Integer("is_active").default(1)  # Boolean as INTEGER in SQLite
    metadata = JSON("metadata").nullable()
    bio = Text("bio").nullable()


class Posts(BaseTable):
    """Example table class for Posts with foreign key to Users."""

    __tablename__ = "posts"

    id = Integer("id").primary_key()
    title = Text("title").not_null()
    content = Text("content").not_null()
    author_id = Integer("author_id").references(Users.id, on_delete="CASCADE")


async def create_tables(sqlite_conn: aiosqlite.Connection) -> None:
    """Create tables in the database using schema generation."""

    # Generate and execute Users table creation
    users_sql = generate_create_table_sql(Users, Dialect.SQLITE)
    print("Generated Users table SQL:")
    print(users_sql)
    print()

    # Replace CREATE TABLE with CREATE TABLE IF NOT EXISTS for safety
    users_sql = users_sql.replace("CREATE TABLE", "CREATE TABLE IF NOT EXISTS")
    await sqlite_conn.execute(users_sql)

    # Generate and execute Posts table creation
    posts_sql = generate_create_table_sql(Posts, Dialect.SQLITE)
    print("Generated Posts table SQL:")
    print(posts_sql)
    print()

    # Replace CREATE TABLE with CREATE TABLE IF NOT EXISTS for safety
    posts_sql = posts_sql.replace("CREATE TABLE", "CREATE TABLE IF NOT EXISTS")
    await sqlite_conn.execute(posts_sql)

    await sqlite_conn.commit()


async def seed_data(sqlite_conn: aiosqlite.Connection) -> None:
    """Seed the database with initial data."""

    await sqlite_conn.executemany(
        """
        INSERT INTO users (name, email, age, is_active, metadata, bio)
        VALUES (?, ?, ?, ?, ?, ?);
        """,
        [
            (
                "Alice",
                "alice@gmail.com",
                30,
                True,
                json.dumps({"hobbies": ["reading", "gaming"]}),
                "Loves reading books.",
            ),
            (
                "Bob",
                "bob@email.com",
                25,
                True,
                json.dumps({"hobbies": ["sports"]}),
                "Enjoys playing football.",
            ),
            ("Charlie", "charlie@test.co.uk", 35, False, None, None),
            (
                "Diana",
                "di@example.org",
                17,
                True,
                json.dumps({"hobbies": ["music", "art"]}),
                "Aspiring artist.",
            ),
        ],
    )

    # Seed posts data
    await sqlite_conn.executemany(
        """
        INSERT INTO posts (title, content, author_id)
        VALUES (?, ?, ?);
        """,
        [
            ("My First Post", "This is Alice's first blog post about reading.", 1),
            ("Football Season", "Bob writes about the upcoming football season.", 2),
            ("Art Exhibition", "Diana shares her thoughts on the local art exhibition.", 4),
            ("Book Review", "Alice reviews her latest favorite novel.", 1),
        ],
    )

    await sqlite_conn.commit()


async def main() -> None:
    # Configure Schemix logging to DEBUG level for console output
    configure_logging(level=logging.DEBUG)

    # Option 1: Using helper function (recommended)
    connection = await create_sqlite_connection(":memory:")

    # Option 2: Manual setup (if you need more control)
    # sqlite_conn = await aiosqlite.connect(":memory:")
    # await sqlite_conn.execute("PRAGMA foreign_keys = ON")
    # await sqlite_conn.commit()
    # connection = SQLiteConnection(sqlite_conn)

    db = Database(connection, [Users, Posts])

    # For table creation, we still need the raw connection
    # This will be improved when we add schema generation
    sqlite_conn = connection._conn
    await create_tables(sqlite_conn)
    await seed_data(sqlite_conn)

    # Example query using the select builder
    query = (
        db.select({"id": Users.id, "name": Users.name, "email": Users.email})
        .from_(Users)
        .where(Users.age > 18)
        .order_by(Users.name)
    )
    results = await query.execute()

    print("Query Results:")
    for row in results:
        print(row)

    # Example of aggregations
    agg_query = (
        db.select(
            {"count": Users.id.count(), "avg_age": Users.age.avg(), "is_active": Users.is_active}
        )
        .from_(Users)
        .group_by(Users.is_active)
    )
    agg_results = await agg_query.execute()

    print("\nAggregation Results:")
    for row in agg_results:
        print(row)

    # Test JOIN operations
    join_query = (
        db.select(
            {"user_name": Users.name, "post_title": Posts.title, "post_content": Posts.content}
        )
        .from_(Users)
        .inner_join(Posts, Users.id == Posts.author_id)
        .where(Users.age > 18)
        .order_by(Users.name, Posts.title)
    )

    sql, params = join_query.get_sql()
    print(f"Generated JOIN SQL: {sql}")
    print(f"Parameters: {params}")

    join_results = await join_query.execute()
    print("\nJOIN Query Results:")
    for row in join_results:
        print(row)

    # Test INSERT operations
    print("\n--- Testing INSERT operations ---")

    # Insert a new user
    insert_result = (
        await db.insert(Users)
        .values(
            {
                "name": "Eve",
                "email": "eve@example.com",
                "age": 28,
                "is_active": 1,
                "metadata": {"hobbies": ["photography", "hiking"]},
                "bio": "Adventure enthusiast",
            }
        )
        .execute()
    )

    print(f"INSERT result: {insert_result}")

    # Insert a new post
    post_insert_result = (
        await db.insert(Posts)
        .values(
            {
                "title": "Photography Tips",
                "content": "Eve shares her best photography tips for beginners.",
                "author_id": 5,  # Assuming Eve will have ID 5
            }
        )
        .execute()
    )

    print(f"Post INSERT result: {post_insert_result}")

    # Verify the inserts worked by querying the new data
    verification_query = (
        db.select({"name": Users.name, "email": Users.email, "post_title": Posts.title})
        .from_(Users)
        .left_join(Posts, Users.id == Posts.author_id)
        .where(Users.name == "Eve")
    )

    verification_results = await verification_query.execute()
    print("\nVerification query results:")
    for row in verification_results:
        print(row)

    # Test bulk INSERT operations
    print("\n--- Testing bulk INSERT operations ---")

    # Insert multiple users at once
    bulk_users = [
        {
            "name": "Frank",
            "email": "frank@example.com",
            "age": 32,
            "is_active": 1,
            "metadata": {"hobbies": ["cooking"]},
            "bio": "Chef enthusiast",
        },
        {
            "name": "Grace",
            "email": "grace@example.com",
            "age": 29,
            "is_active": 1,
            "metadata": {"hobbies": ["dancing", "music"]},
            "bio": "Dance instructor",
        },
        {
            "name": "Henry",
            "email": "henry@example.com",
            "age": 45,
            "is_active": 0,
            "metadata": None,
            "bio": None,
        },
    ]

    bulk_insert_result = await db.insert(Users).values(bulk_users).execute()
    print(f"Bulk INSERT result: {bulk_insert_result}")

    # Insert multiple posts at once
    bulk_posts = [
        {
            "title": "Cooking Tips",
            "content": "Frank shares his favorite cooking techniques.",
            "author_id": 6,  # Frank
        },
        {
            "title": "Dance Lessons",
            "content": "Grace offers beginner dance lessons.",
            "author_id": 7,  # Grace
        },
    ]

    bulk_posts_result = await db.insert(Posts).values(bulk_posts).execute()
    print(f"Bulk posts INSERT result: {bulk_posts_result}")

    # Verify the bulk inserts
    alt_verification_query = (
        db.select({"name": Users.name, "email": Users.email})
        .from_(Users)
        .where((Users.name == "Frank") | (Users.name == "Grace") | (Users.name == "Henry"))
        .order_by(Users.name)
    )
    alt_verification_results = await alt_verification_query.execute()
    print("\nBulk insert verification (alternative):")
    for row in alt_verification_results:
        print(row)

    await sqlite_conn.close()


if __name__ == "__main__":
    asyncio.run(main())
