from playhouse.pool import PooledPostgresqlDatabase
from .config import Config

# Pooled DB voor betere concurrerende requests
db = PooledPostgresqlDatabase(
    Config.PGDATABASE,
    user=Config.PGUSER,
    password=Config.PGPASSWORD,
    host=Config.PGHOST,
    port=Config.PGPORT,
    max_connections=16,
    stale_timeout=300,  # seconden
)
