"""
Redis client for commonlog (Python)
"""

class RedisConfigError(Exception):
    pass

def get_redis_client(config):
    import redis  # Import lazily to avoid distutils issues in Python 3.12+
    provider_config = getattr(config, 'provider_config', {})
    host = provider_config.get('redis_host')
    port = provider_config.get('redis_port')
    password = provider_config.get('redis_password')
    ssl = provider_config.get('redis_ssl', False)
    cluster_mode = provider_config.get('redis_cluster_mode', False)
    db = provider_config.get('redis_db', 0)

    if not host or not port:
        raise RedisConfigError("redis_host and redis_port must be set in provider_config")

    if cluster_mode:
        # Use RedisCluster for cluster mode (ElastiCache with cluster mode enabled)
        try:
            from redis.cluster import RedisCluster
        except ImportError:
            raise RedisConfigError("Redis cluster support is not available. Please upgrade redis package to version 4.0.0 or later")

        # For cluster mode, we need to handle startup nodes differently
        # ElastiCache cluster mode provides a single endpoint
        startup_nodes = [{"host": host, "port": int(port)}]

        return RedisCluster(
            startup_nodes=startup_nodes,
            password=password,
            ssl=ssl,
            decode_responses=True,
            skip_full_coverage_check=True,  # Allow partial cluster access
        )
    else:
        # Standard Redis client for single node or ElastiCache without cluster mode
        return redis.StrictRedis(
            host=host,
            port=int(port),
            password=password,
            db=int(db),
            ssl=ssl,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
        )
