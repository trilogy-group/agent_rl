import asyncio
import asyncpg
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from queue import Queue

logger = logging.getLogger(__name__)

@dataclass 
class AgentExchange:
    """Data structure for tracking complete agent exchanges (legacy)"""
    exchange_id: str
    thread_id: str
    user_query: str
    agent_response: str
    user_followup: Optional[str] = None
    intent: Optional[str] = None
    task_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None
    evaluation_score: Optional[float] = None
    evaluation_feedback: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}

class ExchangeTracker:
    """
    Legacy exchange tracking functionality with evaluation capabilities.
    This code was moved from rl_tracker.py as it's currently unused.
    """
    
    def __init__(self, postgres_url: str = None):
        self.postgres_url = postgres_url or os.getenv('POSTGRES_URL')
        if not self.postgres_url:
            raise ValueError("POSTGRES_URL environment variable is required")
            
        self.exchange_queue = Queue()
        self.pool = None
        
    async def _init_db_pool(self):
        """Initialize database connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                self.postgres_url,
                min_size=2,
                max_size=10,
                command_timeout=30
            )
            await self._create_exchange_table()
            logger.info("Exchange tracker database pool initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            raise
    
    async def _create_exchange_table(self):
        """Create exchange tracking table"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS agent_exchanges (
            id SERIAL PRIMARY KEY,
            exchange_id VARCHAR(255) UNIQUE NOT NULL,
            thread_id VARCHAR(255) NOT NULL,
            user_query TEXT NOT NULL,
            agent_response TEXT NOT NULL,
            user_followup TEXT,
            intent VARCHAR(100),
            task_type VARCHAR(100),
            metadata JSONB DEFAULT '{}',
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            evaluation_score FLOAT,
            evaluation_feedback TEXT,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_exchanges_thread_id ON agent_exchanges(thread_id);
        CREATE INDEX IF NOT EXISTS idx_exchanges_timestamp ON agent_exchanges(timestamp);
        CREATE INDEX IF NOT EXISTS idx_exchanges_task_type ON agent_exchanges(task_type);
        """
        
        async with self.pool.acquire() as conn:
            await conn.execute(create_table_sql)
            logger.info("Exchange tracking table created/verified")

    async def _store_exchange(self, exchange: AgentExchange):
        """Store exchange in database"""
        try:
            insert_sql = """
            INSERT INTO agent_exchanges (
                exchange_id, thread_id, user_query, agent_response, user_followup,
                intent, task_type, timestamp, metadata, evaluation_score, evaluation_feedback
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            ON CONFLICT (exchange_id) 
            DO UPDATE SET
                user_followup = EXCLUDED.user_followup,
                evaluation_score = EXCLUDED.evaluation_score,
                evaluation_feedback = EXCLUDED.evaluation_feedback,
                updated_at = NOW()
            """
            
            async with self.pool.acquire() as conn:
                await conn.execute(
                    insert_sql,
                    exchange.exchange_id,
                    exchange.thread_id,
                    exchange.user_query,
                    exchange.agent_response,
                    exchange.user_followup,
                    exchange.intent,
                    exchange.task_type,
                    exchange.timestamp,
                    json.dumps(exchange.metadata),
                    exchange.evaluation_score,
                    exchange.evaluation_feedback
                )
                
            logger.info(f"Stored exchange {exchange.exchange_id}")
            
        except Exception as e:
            logger.error(f"Failed to store exchange {exchange.exchange_id}: {e}")
    
    async def _evaluate_exchange(self, exchange: AgentExchange):
        """Evaluate the quality of an agent exchange"""
        try:
            # Simple heuristic evaluation - can be enhanced with ML models
            score = self._calculate_basic_score(exchange)
            feedback = self._generate_basic_feedback(exchange, score)
            
            # Update exchange with evaluation
            exchange.evaluation_score = score
            exchange.evaluation_feedback = feedback
            
            # Update in database
            update_sql = """
            UPDATE agent_exchanges 
            SET evaluation_score = $1, evaluation_feedback = $2, updated_at = NOW()
            WHERE exchange_id = $3
            """
            
            async with self.pool.acquire() as conn:
                await conn.execute(update_sql, score, feedback, exchange.exchange_id)
                
            logger.info(f"Evaluated exchange {exchange.exchange_id} with score {score}")
            
        except Exception as e:
            logger.error(f"Failed to evaluate exchange {exchange.exchange_id}: {e}")
    
    def _calculate_basic_score(self, exchange: AgentExchange) -> float:
        """Calculate basic satisfaction score based on followup content"""
        if not exchange.user_followup:
            return 0.5  # Neutral if no followup
            
        followup_lower = exchange.user_followup.lower()
        
        # Positive indicators
        positive_words = [
            'thanks', 'thank you', 'perfect', 'great', 'excellent', 'good',
            'helpful', 'useful', 'exactly', 'love it', 'awesome', 'fantastic'
        ]
        
        # Negative indicators
        negative_words = [
            'wrong', 'bad', 'terrible', 'useless', 'horrible', 'fix',
            'error', 'mistake', 'not what', 'disappointed', 'awful'
        ]
        
        # Improvement request indicators (neutral to positive)
        improvement_words = [
            'make it', 'can you', 'please', 'could you', 'add', 'change',
            'modify', 'improve', 'better', 'more', 'less'
        ]
        
        positive_count = sum(1 for word in positive_words if word in followup_lower)
        negative_count = sum(1 for word in negative_words if word in followup_lower)
        improvement_count = sum(1 for word in improvement_words if word in followup_lower)
        
        # Calculate score (0.0 to 1.0)
        if negative_count > positive_count:
            return max(0.1, 0.3 - (negative_count * 0.1))
        elif positive_count > 0:
            return min(1.0, 0.7 + (positive_count * 0.1))
        elif improvement_count > 0:
            return 0.6  # Neutral-positive for improvement requests
        else:
            return 0.5  # Neutral
    
    def _generate_basic_feedback(self, exchange: AgentExchange, score: float) -> str:
        """Generate basic feedback based on evaluation"""
        if score >= 0.8:
            return "High satisfaction - User expressed positive feedback"
        elif score >= 0.6:
            return "Good satisfaction - User showed engagement or requested improvements"
        elif score >= 0.4:
            return "Neutral satisfaction - Mixed or unclear user response"
        else:
            return "Low satisfaction - User expressed dissatisfaction or reported issues"
    
    def track_exchange(self, exchange_id: str, thread_id: str, user_query: str, 
                      agent_response: str, intent: str = None, task_type: str = None,
                      metadata: Dict[str, Any] = None):
        """Track a new agent exchange (minimal interface for graph nodes)"""
        exchange = AgentExchange(
            exchange_id=exchange_id,
            thread_id=thread_id,
            user_query=user_query,
            agent_response=agent_response,
            intent=intent,
            task_type=task_type,
            metadata=metadata or {}
        )
        
        self.exchange_queue.put(exchange)
        logger.debug(f"Queued exchange {exchange_id} for processing")
    
    def update_followup(self, exchange_id: str, user_followup: str):
        """Update an exchange with user followup (triggers evaluation)"""
        # Create update exchange with followup
        # This is a simplified approach - in production you might want to 
        # fetch the existing exchange and update it
        temp_exchange = AgentExchange(
            exchange_id=exchange_id,
            thread_id="",  # Will be ignored in update
            user_query="",  # Will be ignored in update
            agent_response="",  # Will be ignored in update
            user_followup=user_followup
        )
        
        self.exchange_queue.put(temp_exchange)
        logger.debug(f"Queued followup update for exchange {exchange_id}")
    
    async def get_exchange_stats(self, days: int = 7) -> Dict[str, Any]:
        """Get exchange statistics for analysis"""
        try:
            stats_sql = """
            SELECT 
                COUNT(*) as total_exchanges,
                AVG(evaluation_score) as avg_score,
                COUNT(CASE WHEN evaluation_score >= 0.8 THEN 1 END) as high_satisfaction,
                COUNT(CASE WHEN evaluation_score < 0.4 THEN 1 END) as low_satisfaction,
                task_type,
                COUNT(*) as count_by_task
            FROM agent_exchanges 
            WHERE timestamp >= NOW() - INTERVAL '%s days'
            GROUP BY task_type
            """
            
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(stats_sql, days)
                
            return {
                'period_days': days,
                'stats_by_task': [dict(row) for row in rows]
            }
            
        except Exception as e:
            logger.error(f"Failed to get exchange stats: {e}")
            return {}

# Convenience functions for exchange tracking
def track_agent_exchange(exchange_id: str, thread_id: str, user_query: str, 
                        agent_response: str, intent: str = None, task_type: str = None,
                        metadata: Dict[str, Any] = None):
    """Convenience function for tracking exchanges (legacy - unused)"""
    # This would need to be connected to an ExchangeTracker instance
    pass

def track_user_followup(exchange_id: str, user_followup: str):
    """Convenience function for tracking user followups (legacy - unused)"""
    # This would need to be connected to an ExchangeTracker instance
    pass