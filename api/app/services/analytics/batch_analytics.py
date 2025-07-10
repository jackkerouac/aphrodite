"""
Batch Analytics Service

Provides analytics for batch operations including aggregated stats,
performance metrics, and parent-child activity relationships.
"""

from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from datetime import datetime, timedelta

from app.models.media_activity import MediaActivityModel
from app.models.badge_application import BadgeApplicationModel
from app.models.poster_replacement import PosterReplacementModel
from app.models.activity_performance_metric import ActivityPerformanceMetricModel


class BatchAnalyticsService:
    """Service for analyzing batch operations and activity relationships"""
    
    async def get_batch_summary(
        self,
        batch_job_id: str,
        db_session: AsyncSession
    ) -> Dict[str, Any]:
        """
        Get comprehensive summary for a specific batch job.
        
        Returns success/failure counts, timing, performance metrics.
        """
        try:
            # Get all activities for this batch
            query = select(MediaActivityModel).where(
                MediaActivityModel.batch_job_id == batch_job_id
            ).order_by(MediaActivityModel.created_at)
            
            result = await db_session.execute(query)
            activities = result.scalars().all()
            
            if not activities:
                return {
                    "batch_job_id": batch_job_id,
                    "found": False,
                    "error": "No activities found for this batch job ID"
                }
            
            # Calculate basic statistics
            total_activities = len(activities)
            successful = sum(1 for a in activities if a.success is True)
            failed = sum(1 for a in activities if a.success is False)
            pending = sum(1 for a in activities if a.success is None)
            
            # Calculate timing
            start_time = min(a.created_at for a in activities if a.created_at)
            end_time = max(a.completed_at for a in activities if a.completed_at)
            
            total_duration = None
            if start_time and end_time:
                total_duration = int((end_time - start_time).total_seconds() * 1000)
            
            # Calculate average processing time
            processing_times = [a.processing_duration_ms for a in activities if a.processing_duration_ms]
            avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else None
            
            # Activity type breakdown
            activity_types = {}
            for activity in activities:
                activity_type = activity.activity_type
                if activity_type not in activity_types:
                    activity_types[activity_type] = {"total": 0, "successful": 0, "failed": 0}
                
                activity_types[activity_type]["total"] += 1
                if activity.success is True:
                    activity_types[activity_type]["successful"] += 1
                elif activity.success is False:
                    activity_types[activity_type]["failed"] += 1
            
            # Get error summary
            error_summary = {}
            for activity in activities:
                if activity.error_message:
                    error_msg = activity.error_message[:100]  # Truncate long errors
                    error_summary[error_msg] = error_summary.get(error_msg, 0) + 1
            
            return {
                "batch_job_id": batch_job_id,
                "found": True,
                "summary": {
                    "total_activities": total_activities,
                    "successful": successful,
                    "failed": failed,
                    "pending": pending,
                    "success_rate": round(successful / total_activities * 100, 2) if total_activities > 0 else 0
                },
                "timing": {
                    "start_time": start_time.isoformat() if start_time else None,
                    "end_time": end_time.isoformat() if end_time else None,
                    "total_duration_ms": total_duration,
                    "average_processing_time_ms": round(avg_processing_time) if avg_processing_time else None
                },
                "activity_breakdown": activity_types,
                "error_summary": error_summary,
                "activities": [
                    {
                        "activity_id": str(activity.id),
                        "media_id": activity.media_id,
                        "activity_type": activity.activity_type,
                        "status": activity.status,
                        "success": activity.success,
                        "created_at": activity.created_at.isoformat() if activity.created_at else None,
                        "processing_duration_ms": activity.processing_duration_ms,
                        "error_message": activity.error_message
                    } for activity in activities
                ]
            }
            
        except Exception as e:
            return {
                "batch_job_id": batch_job_id,
                "found": False,
                "error": f"Failed to analyze batch: {str(e)}"
            }
    
    async def get_batch_performance_analytics(
        self,
        batch_job_id: str,
        db_session: AsyncSession
    ) -> Dict[str, Any]:
        """
        Get performance analytics for a batch job.
        
        Includes resource usage, bottlenecks, and performance trends.
        """
        try:
            # Get performance metrics for all activities in the batch
            query = select(
                MediaActivityModel.activity_type,
                ActivityPerformanceMetricModel.cpu_usage_percent,
                ActivityPerformanceMetricModel.memory_usage_mb,
                ActivityPerformanceMetricModel.disk_io_read_mb,
                ActivityPerformanceMetricModel.disk_io_write_mb,
                ActivityPerformanceMetricModel.throughput_items_per_second,
                ActivityPerformanceMetricModel.bottleneck_stage,
                ActivityPerformanceMetricModel.server_load_average
            ).select_from(
                MediaActivityModel.__table__.join(
                    ActivityPerformanceMetricModel.__table__,
                    MediaActivityModel.id == ActivityPerformanceMetricModel.activity_id
                )
            ).where(
                MediaActivityModel.batch_job_id == batch_job_id
            )
            
            result = await db_session.execute(query)
            metrics = result.fetchall()
            
            if not metrics:
                return {
                    "batch_job_id": batch_job_id,
                    "found": False,
                    "message": "No performance metrics found for this batch"
                }
            
            # Calculate aggregated performance metrics
            cpu_values = [float(m.cpu_usage_percent) for m in metrics if m.cpu_usage_percent]
            memory_values = [float(m.memory_usage_mb) for m in metrics if m.memory_usage_mb]
            disk_read_values = [float(m.disk_io_read_mb) for m in metrics if m.disk_io_read_mb]
            disk_write_values = [float(m.disk_io_write_mb) for m in metrics if m.disk_io_write_mb]
            throughput_values = [float(m.throughput_items_per_second) for m in metrics if m.throughput_items_per_second]
            load_values = [float(m.server_load_average) for m in metrics if m.server_load_average]
            
            # Bottleneck analysis
            bottlenecks = {}
            for metric in metrics:
                if metric.bottleneck_stage:
                    bottlenecks[metric.bottleneck_stage] = bottlenecks.get(metric.bottleneck_stage, 0) + 1
            
            performance_summary = {
                "batch_job_id": batch_job_id,
                "found": True,
                "metrics_count": len(metrics),
                "resource_usage": {
                    "cpu": {
                        "average": round(sum(cpu_values) / len(cpu_values), 2) if cpu_values else None,
                        "peak": max(cpu_values) if cpu_values else None,
                        "minimum": min(cpu_values) if cpu_values else None
                    },
                    "memory": {
                        "average_mb": round(sum(memory_values) / len(memory_values), 2) if memory_values else None,
                        "peak_mb": max(memory_values) if memory_values else None,
                        "minimum_mb": min(memory_values) if memory_values else None
                    },
                    "disk_io": {
                        "total_read_mb": round(sum(disk_read_values), 2) if disk_read_values else None,
                        "total_write_mb": round(sum(disk_write_values), 2) if disk_write_values else None,
                        "average_read_mb": round(sum(disk_read_values) / len(disk_read_values), 2) if disk_read_values else None,
                        "average_write_mb": round(sum(disk_write_values) / len(disk_write_values), 2) if disk_write_values else None
                    },
                    "throughput": {
                        "average_items_per_second": round(sum(throughput_values) / len(throughput_values), 2) if throughput_values else None,
                        "peak_items_per_second": max(throughput_values) if throughput_values else None
                    },
                    "system_load": {
                        "average": round(sum(load_values) / len(load_values), 2) if load_values else None,
                        "peak": max(load_values) if load_values else None
                    }
                },
                "bottleneck_analysis": [
                    {"stage": stage, "frequency": count}
                    for stage, count in sorted(bottlenecks.items(), key=lambda x: x[1], reverse=True)
                ]
            }
            
            return performance_summary
            
        except Exception as e:
            return {
                "batch_job_id": batch_job_id,
                "found": False,
                "error": f"Failed to analyze batch performance: {str(e)}"
            }
    
    async def get_recent_batches(
        self,
        days: int = 7,
        limit: int = 20,
        db_session: AsyncSession
    ) -> List[Dict[str, Any]]:
        """
        Get summary of recent batch operations.
        """
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get recent batch jobs
            query = select(
                MediaActivityModel.batch_job_id,
                func.count(MediaActivityModel.id).label('total_activities'),
                func.sum(func.case([(MediaActivityModel.success == True, 1)], else_=0)).label('successful'),
                func.sum(func.case([(MediaActivityModel.success == False, 1)], else_=0)).label('failed'),
                func.min(MediaActivityModel.created_at).label('start_time'),
                func.max(MediaActivityModel.completed_at).label('end_time'),
                func.avg(MediaActivityModel.processing_duration_ms).label('avg_processing_time')
            ).where(
                and_(
                    MediaActivityModel.batch_job_id.isnot(None),
                    MediaActivityModel.created_at >= start_date
                )
            ).group_by(
                MediaActivityModel.batch_job_id
            ).order_by(
                desc(func.min(MediaActivityModel.created_at))
            ).limit(limit)
            
            result = await db_session.execute(query)
            batch_data = result.fetchall()
            
            batches = []
            for row in batch_data:
                total = row.total_activities or 0
                successful = row.successful or 0
                failed = row.failed or 0
                
                batch_duration = None
                if row.start_time and row.end_time:
                    batch_duration = int((row.end_time - row.start_time).total_seconds() * 1000)
                
                batches.append({
                    "batch_job_id": row.batch_job_id,
                    "total_activities": total,
                    "successful": successful,
                    "failed": failed,
                    "pending": total - successful - failed,
                    "success_rate": round(successful / total * 100, 2) if total > 0 else 0,
                    "start_time": row.start_time.isoformat() if row.start_time else None,
                    "end_time": row.end_time.isoformat() if row.end_time else None,
                    "batch_duration_ms": batch_duration,
                    "average_processing_time_ms": round(float(row.avg_processing_time)) if row.avg_processing_time else None
                })
            
            return batches
            
        except Exception as e:
            raise Exception(f"Failed to retrieve recent batches: {str(e)}")


def get_batch_analytics_service() -> BatchAnalyticsService:
    """Get singleton instance of BatchAnalyticsService"""
    if not hasattr(get_batch_analytics_service, '_instance'):
        get_batch_analytics_service._instance = BatchAnalyticsService()
    return get_batch_analytics_service._instance
