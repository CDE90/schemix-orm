import asyncio
import json

import aiosqlite

from schemix.columns import JSON, Boolean, Integer, Text, Varchar
from schemix.database import Database
from schemix.helpers import create_sqlite_connection
from schemix.table import BaseTable


class Users(BaseTable):
    """Example table class for Users."""

    __tablename__ = "users"

    id = Integer("id").primary_key()
    name = Varchar("name", length=100).not_null()
    email = Varchar("email", length=100).not_null().unique()
    age = Integer("age").not_null()
    is_active = Boolean("is_active").default(True)
    metadata = JSON("metadata").nullable()
    bio = Text("bio").nullable()


async def create_tables(sqlite_conn: aiosqlite.Connection) -> None:
    """Create tables in the database."""

    # For now, we manually create the table.
    await sqlite_conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            age INTEGER NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            metadata JSON,
            bio TEXT
        );
        """
    )
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
    await sqlite_conn.commit()


async def main() -> None:
    # Option 1: Using helper function (recommended)
    connection = await create_sqlite_connection(":memory:")

    # Option 2: Manual setup (if you need more control)
    # sqlite_conn = await aiosqlite.connect(":memory:")
    # await sqlite_conn.execute("PRAGMA foreign_keys = ON")
    # await sqlite_conn.commit()
    # connection = SQLiteConnection(sqlite_conn)

    db = Database(connection, [Users])

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

    await sqlite_conn.close()


if __name__ == "__main__":
    asyncio.run(main())
