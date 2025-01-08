# backend/app/models/base.py
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import URL
import logging
from contextlib import contextmanager
from typing import Generator
from ..core.config import get_settings
from sqlalchemy.schema import CreateTable, DropTable
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.ddl import CreateSchema, DropSchema
import enum
import threading
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

def create_enum_type(enum_class):
    """
    Create a PostgreSQL enum type for a Python enum class
    
    Args:
        enum_class (Type[Enum]): Enum class to convert to PostgreSQL enum
    
    Returns:
        Tuple of SQL statements for checking, dropping, and creating enum
    """
    values = [e.value for e in enum_class]
    enum_name = enum_class.__name__.lower()
    
    check_exists = text(f"""
        SELECT EXISTS (
            SELECT 1
            FROM pg_type
            WHERE typname = '{enum_name}'
        );
    """)
    
    drop_type = text(f"""
        DROP TYPE IF EXISTS {enum_name} CASCADE;
    """)
    
    create_type = text(f"""
        CREATE TYPE {enum_name} AS ENUM {str(tuple(values))};
    """)
    
    return check_exists, drop_type, create_type

# Create Base class first
Base = declarative_base()

class DatabaseManager:
    """
    Manages database connections and security settings
    """
    def __init__(self):
        self._engine = None
        self._session_factory = None
        self._connection_semaphore = threading.Semaphore(10)
        self.Base = Base  # Use the already created Base

    @property
    def engine(self):
        """Lazy initialization of database engine"""
        if self._engine is None:
            self._engine = create_engine(
                settings.DATABASE_URL,
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=1800,
                pool_pre_ping=True,
                connect_args={
                    "connect_timeout": 10,
                    "application_name": "pintar_ekspor",
                    "client_encoding": "utf8",
                    "options": "-c statement_timeout=30000"
                }
            )
            self._setup_engine_events()
        return self._engine

    @property
    def session_factory(self):
        """Lazy initialization of session factory"""
        if self._session_factory is None:
            self._session_factory = scoped_session(
                sessionmaker(
                    autocommit=False,
                    autoflush=False,
                    bind=self.engine
                )
            )
        return self._session_factory

    def _setup_engine_events(self):
        """Set up SQLAlchemy engine events"""
        @event.listens_for(self.engine, 'connect')
        def on_connect(dbapi_connection, connection_record):
            """Set up connection-level security"""
            with dbapi_connection.cursor() as cursor:
                cursor.execute("SET statement_timeout = 30000")
                cursor.execute("SET idle_in_transaction_session_timeout = 60000")
                cursor.execute("SET client_encoding = 'UTF8'")

        @event.listens_for(self.engine, 'checkout')
        def on_checkout(dbapi_connection, connection_record, connection_proxy):
            """Verify connection on checkout"""
            # Check connection age
            connection_record.info.setdefault('checkout_time', time.time())
            if time.time() - connection_record.info['checkout_time'] > 1800:
                # Recycle connections older than 30 minutes
                raise Exception("Connection too old")

            # Verify connection is still valid
            try:
                # Use cursor execute for connection test instead of ping
                cursor = dbapi_connection.cursor()
                cursor.execute('SELECT 1')
                cursor.close()
            except Exception:
                raise Exception("Database connection invalid")

    @contextmanager
    def get_db(self) -> Generator:
        """
        Get database session with connection limiting and error handling
        """
        acquired = self._connection_semaphore.acquire(timeout=10)
        if not acquired:
            raise Exception("Could not acquire database connection")

        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database error: {str(e)}")
            raise
        finally:
            session.close()
            self._connection_semaphore.release()

    def init_db(self):
        """Initialize database with security measures"""
        try:
            # Import here to avoid circular imports
            from ..models.user import UserRole
            from ..core.audit import setup_audit_listeners
            
            # Set up audit logging
            setup_audit_listeners()
            
            # Create all tables
            self.Base.metadata.create_all(bind=self.engine)
            
            # Create a connection
            with self.engine.connect() as connection:
                # Get SQL statements for enum creation
                check_exists, drop_type, create_type = create_enum_type(UserRole)
                
                # Check if enum exists
                result = connection.execute(check_exists)
                exists = result.scalar()
                
                if exists:
                    connection.execute(drop_type)
                
                # Create new enum
                connection.execute(create_type)
                
                # Set up row-level security
                connection.execute(text("""
                    ALTER TABLE users ENABLE ROW LEVEL SECURITY;
                    CREATE POLICY user_isolation_policy ON users
                        USING (id = current_user_id());
                """))
                
                logger.info("Successfully configured database security")
            
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise

# Create global database manager instance
db_manager = DatabaseManager()

# Dependency for FastAPI
def get_db():
    """Database session dependency"""
    with db_manager.get_db() as session:
        yield session

# Additional compilation customization if needed
@compiles(CreateSchema)
def _create_schema(element, compiler, **kw):
    return f"CREATE SCHEMA IF NOT EXISTS {compiler.preparer.format_schema(element.name)}"

@compiles(DropSchema)
def _drop_schema(element, compiler, **kw):
    return f"DROP SCHEMA IF EXISTS {compiler.preparer.format_schema(element.name)} CASCADE"

# Export engine for other modules to use
engine = db_manager.engine