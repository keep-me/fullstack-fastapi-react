"""
Password utilities for the application.
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=10)
test_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=4)
_thread_pool = ThreadPoolExecutor(max_workers=4, thread_name_prefix="password_hash")


async def get_password_hash_async(password: str) -> str:
    """
    Hash password asynchronously.
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_thread_pool, pwd_context.hash, password)


def get_password_hash_fast(password: str) -> str:
    """
    Hash password with fast settings for tests.
    """
    return test_pwd_context.hash(password)


async def get_password_hash_fast_async(password: str) -> str:
    """
    Hash password asynchronously with fast settings for tests.
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_thread_pool, test_pwd_context.hash, password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify plain password against hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)
