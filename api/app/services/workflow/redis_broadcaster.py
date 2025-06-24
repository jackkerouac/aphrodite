"""
Redis Progress Broadcaster

Cross-process communication for progress updates using Redis pub/sub.
"""

import json
import asyncio
from typing import Optional, Dict, Any
import redis.asyncio as redis
from aphrodite_logging import get_logger
from app.core.config import get_settings

logger = get_logger("aphrodite.workflow.redis_broadcaster")


class RedisProgressBroadcaster:
    """Redis-based progress broadcaster for cross-process communication"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.pubsub: Optional[redis.client.PubSub] = None
        self.is_listening = False
        self.settings = get_settings()
    
    async def initialize(self):
        """Initialize Redis connection"""
        try:
            # Parse Redis URL to handle both redis:// and plain host:port formats
            redis_url = self.settings.redis_url or "redis://localhost:6379/0"
            
            self.redis_client = redis.from_url(
                redis_url,
                encoding='utf-8',
                decode_responses=True
            )
            
            # Test connection
            await self.redis_client.ping()
            logger.info("Redis progress broadcaster initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis progress broadcaster: {e}")
            self.redis_client = None
    
    async def publish_progress_update(self, job_id: str, progress_data: Dict[str, Any]):
        """Publish progress update to Redis"""
        if not self.redis_client:
            logger.warning("Redis client not initialized - cannot publish progress update")
            return
        
        try:
            channel = f"job_progress:{job_id}"
            message = {
                "type": "progress_update",
                "job_id": job_id,
                "data": progress_data,
                "timestamp": asyncio.get_event_loop().time()
            }
            
            await self.redis_client.publish(channel, json.dumps(message))
            logger.info(f"Published progress update to Redis for job {job_id}")
            
        except Exception as e:
            logger.error(f"Failed to publish progress update for job {job_id}: {e}")
    
    async def subscribe_to_progress_updates(self, callback):
        """Subscribe to all progress updates and call callback"""
        if not self.redis_client:
            logger.warning("Redis client not initialized - cannot subscribe to progress updates")
            return
        
        try:
            self.pubsub = self.redis_client.pubsub()
            await self.pubsub.psubscribe("job_progress:*")
            self.is_listening = True
            
            logger.info("Subscribed to Redis progress updates")
            
            async for message in self.pubsub.listen():
                if message['type'] == 'pmessage':
                    try:
                        data = json.loads(message['data'])
                        job_id = data.get('job_id')
                        if job_id:
                            await callback(job_id, data)
                    except Exception as e:
                        logger.error(f"Failed to process Redis progress message: {e}")
                        
        except Exception as e:
            logger.error(f"Redis subscription error: {e}")
        finally:
            self.is_listening = False
            if self.pubsub:
                await self.pubsub.unsubscribe()
    
    async def close(self):
        """Close Redis connections"""
        self.is_listening = False
        
        if self.pubsub:
            await self.pubsub.unsubscribe()
            await self.pubsub.close()
        
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("Redis progress broadcaster closed")


# Global instance
_redis_broadcaster: Optional[RedisProgressBroadcaster] = None


async def get_redis_broadcaster() -> RedisProgressBroadcaster:
    """Get global Redis broadcaster instance"""
    global _redis_broadcaster
    
    if _redis_broadcaster is None:
        _redis_broadcaster = RedisProgressBroadcaster()
        await _redis_broadcaster.initialize()
    
    return _redis_broadcaster


async def publish_progress_update(job_id: str, progress_data: Dict[str, Any]):
    """Convenience function to publish progress update"""
    broadcaster = await get_redis_broadcaster()
    await broadcaster.publish_progress_update(job_id, progress_data)
