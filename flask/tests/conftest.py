import pytest
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

@pytest.fixture(scope="session")
def test_db():
    """Create test database and tables"""
    load_dotenv()
    
    # Use test database configuration
    TEST_DB_HOST = os.environ.get("TEST_DB_HOST", "localhost")
    TEST_DB_NAME = os.environ.get("TEST_DB_NAME", "test_empowerplant")
    TEST_DB_USER = os.environ.get("TEST_DB_USER", "postgres")
    TEST_DB_PASS = os.environ.get("TEST_DB_PASS", "postgres")
    
    # Create test database engine
    engine = create_engine(
        f'postgresql://{TEST_DB_USER}:{TEST_DB_PASS}@{TEST_DB_HOST}:5432/{TEST_DB_NAME}'
    )
    
    # Create tables
    with engine.connect() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id SERIAL PRIMARY KEY,
            sku VARCHAR NOT NULL,
            count INTEGER NOT NULL,
            productid INTEGER
        )
        """)
        
        # Add test data
        conn.execute("""
        INSERT INTO inventory (sku, count, productid) 
        VALUES ('test123', 5, 3)
        ON CONFLICT DO NOTHING
        """)
    
    yield engine
    
    # Cleanup after tests
    with engine.connect() as conn:
        conn.execute("DELETE FROM inventory")