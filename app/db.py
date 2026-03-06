import asyncpg
from asyncpg import Pool, Record

_pool: Pool | None = None


def _get_pool() -> Pool:
    if _pool is None:
        raise RuntimeError("Database pool is not initialized")
    return _pool


async def connect(dsn: str) -> None:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(dsn=dsn, min_size=1, max_size=10)


async def close() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


async def init_schema() -> None:
    query = """
    CREATE TABLE IF NOT EXISTS requests (
        id BIGSERIAL PRIMARY KEY,
        user_id BIGINT NOT NULL,
        username TEXT,
        full_name TEXT NOT NULL,
        phone TEXT NOT NULL,
        service TEXT NOT NULL,
        preferred_time TEXT NOT NULL,
        comment TEXT,
        status TEXT NOT NULL DEFAULT 'new',
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    CREATE INDEX IF NOT EXISTS idx_requests_status ON requests(status);
    """
    pool = _get_pool()
    async with pool.acquire() as conn:
        await conn.execute(query)


async def insert_request(
    user_id: int,
    username: str | None,
    full_name: str,
    phone: str,
    service: str,
    preferred_time: str,
    comment: str | None,
) -> int:
    query = """
    INSERT INTO requests (user_id, username, full_name, phone, service, preferred_time, comment)
    VALUES ($1, $2, $3, $4, $5, $6, $7)
    RETURNING id;
    """
    pool = _get_pool()
    async with pool.acquire() as conn:
        request_id = await conn.fetchval(
            query, user_id, username, full_name, phone, service, preferred_time, comment
        )
    return int(request_id)


async def update_request_status(request_id: int, status: str) -> bool:
    query = """
    UPDATE requests
    SET status = $2, updated_at = NOW()
    WHERE id = $1;
    """
    pool = _get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute(query, request_id, status)
    return result.endswith("1")


async def get_request(request_id: int) -> Record | None:
    query = "SELECT * FROM requests WHERE id = $1;"
    pool = _get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchrow(query, request_id)


async def get_pending_requests(limit: int = 20) -> list[Record]:
    query = """
    SELECT *
    FROM requests
    WHERE status = 'new'
    ORDER BY created_at ASC
    LIMIT $1;
    """
    pool = _get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(query, limit)
    return list(rows)
