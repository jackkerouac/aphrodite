"""
Enhanced Processing History Reports for Aphrodite Database Tracking

Provides comprehensive reporting capabilities including:
- Success/failure analysis with trends
- Processing time analysis and optimization insights
- Review score distributions and patterns
- Most common errors and troubleshooting
- Export capabilities for external analysis
"""

import sqlite3
import json
import csv
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict, Counter

class ProcessingHistoryReporter:
    """Enhanced reporting for processing history and analytics"""
    
    def __init__(self, db_path="data/aphrodite.db"):
        self.db_path = db_path
    
    def _get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def generate_comprehensive_report(self, library_id: Optional[str] = None, 
                                    days_back: int = 30) -> Dict[str, Any]:
        """
        Generate comprehensive processing report with trends and insights
        
        Args:
            library_id: Filter by library ID (None for all libraries)
            days_back: Number of days to analyze (default 30)
            
        Returns:
            Comprehensive report dictionary
        """
        conn = self._get_connection()
        
        try:
            # Date filter
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            # Base query conditions
            where_conditions = ["last_processed_at >= ?"]
            params = [cutoff_date.isoformat()]
            
            if library_id:
                where_conditions.append("jellyfin_library_id = ?")
                params.append(library_id)
            
            where_clause = " AND ".join(where_conditions)
            
            report = {
                "generated_at": datetime.now().isoformat(),
                "period_analyzed": f"{days_back} days",
                "library_filter": library_id or "All libraries",
                "summary": {},
                "performance": {},
                "errors": {},
                "reviews": {},
                "trends": {},
                "recommendations": []
            }
            
            # Summary statistics
            report["summary"] = self._get_summary_stats(conn, where_clause, params)
            
            # Performance analysis
            report["performance"] = self._get_performance_analysis(conn, where_clause, params)
            
            # Error analysis
            report["errors"] = self._get_error_analysis(conn, where_clause, params)
            
            # Review analysis
            report["reviews"] = self._get_review_analysis(conn, where_clause, params)
            
            # Trend analysis
            report["trends"] = self._get_trend_analysis(conn, where_clause, params, days_back)
            
            # Generate recommendations
            report["recommendations"] = self._generate_recommendations(report)
            
            return report
            
        finally:
            conn.close()
    
    def _get_summary_stats(self, conn, where_clause: str, params: List) -> Dict[str, Any]:
        """Get summary statistics"""
        
        query = f"""
        SELECT 
            COUNT(*) as total_processed,
            COUNT(CASE WHEN last_processing_status = 'success' THEN 1 END) as successful,
            COUNT(CASE WHEN last_processing_status = 'failed' THEN 1 END) as failed,
            COUNT(CASE WHEN last_processing_status = 'partial_success' THEN 1 END) as partial,
            COUNT(DISTINCT jellyfin_library_id) as libraries_processed,
            COUNT(DISTINCT item_type) as item_types_processed,
            AVG(last_processing_duration) as avg_processing_time,
            SUM(last_processing_duration) as total_processing_time,
            MIN(last_processed_at) as earliest_processing,
            MAX(last_processed_at) as latest_processing
        FROM processed_items 
        WHERE {where_clause}
        """
        
        cursor = conn.execute(query, params)
        row = cursor.fetchone()
        
        if not row or row[0] == 0:
            return {"total_processed": 0, "message": "No items processed in specified period"}
        
        total = row[0]
        successful = row[1] or 0
        failed = row[2] or 0
        partial = row[3] or 0
        
        return {
            "total_processed": total,
            "successful": successful,
            "failed": failed,
            "partial_success": partial,
            "success_rate": round((successful / total) * 100, 2) if total > 0 else 0,
            "failure_rate": round((failed / total) * 100, 2) if total > 0 else 0,
            "libraries_processed": row[4] or 0,
            "item_types_processed": row[5] or 0,
            "avg_processing_time": round(row[6] or 0, 2),
            "total_processing_time": round(row[7] or 0, 2),
            "processing_period": {
                "earliest": row[8],
                "latest": row[9]
            }
        }
    
    def _get_performance_analysis(self, conn, where_clause: str, params: List) -> Dict[str, Any]:
        """Analyze processing performance"""
        
        # Processing time by item type (removing MEDIAN as it's not available in SQLite)
        type_query = f"""
        SELECT 
            item_type,
            COUNT(*) as count,
            AVG(last_processing_duration) as avg_time,
            MIN(last_processing_duration) as min_time,
            MAX(last_processing_duration) as max_time
        FROM processed_items 
        WHERE {where_clause} AND last_processing_duration IS NOT NULL
        GROUP BY item_type
        ORDER BY avg_time DESC
        """
        
        cursor = conn.execute(type_query, params)
        by_type = []
        for row in cursor.fetchall():
            by_type.append({
                "item_type": row[0],
                "count": row[1],
                "avg_time": round(row[2], 2),
                "min_time": round(row[3], 2),
                "max_time": round(row[4], 2),
                "median_time": 0  # SQLite doesn't have MEDIAN, set to 0
            })
        
        # Processing time distribution
        distribution_query = f"""
        SELECT 
            CASE 
                WHEN last_processing_duration < 1 THEN 'Under 1s'
                WHEN last_processing_duration < 5 THEN '1-5s'
                WHEN last_processing_duration < 15 THEN '5-15s'
                WHEN last_processing_duration < 30 THEN '15-30s'
                WHEN last_processing_duration < 60 THEN '30-60s'
                ELSE 'Over 60s'
            END as time_bucket,
            COUNT(*) as count
        FROM processed_items 
        WHERE {where_clause} AND last_processing_duration IS NOT NULL
        GROUP BY time_bucket
        ORDER BY 
            CASE 
                WHEN time_bucket = 'Under 1s' THEN 1
                WHEN time_bucket = '1-5s' THEN 2
                WHEN time_bucket = '5-15s' THEN 3
                WHEN time_bucket = '15-30s' THEN 4
                WHEN time_bucket = '30-60s' THEN 5
                ELSE 6
            END
        """
        
        cursor = conn.execute(distribution_query, params)
        time_distribution = [{"bucket": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        # Slowest items
        slowest_query = f"""
        SELECT title, item_type, last_processing_duration, last_processed_at
        FROM processed_items 
        WHERE {where_clause} AND last_processing_duration IS NOT NULL
        ORDER BY last_processing_duration DESC
        LIMIT 10
        """
        
        cursor = conn.execute(slowest_query, params)
        slowest_items = []
        for row in cursor.fetchall():
            slowest_items.append({
                "title": row[0],
                "item_type": row[1],
                "duration": round(row[2], 2),
                "processed_at": row[3]
            })
        
        return {
            "by_item_type": by_type,
            "time_distribution": time_distribution,
            "slowest_items": slowest_items
        }
    
    def _get_error_analysis(self, conn, where_clause: str, params: List) -> Dict[str, Any]:
        """Analyze processing errors"""
        
        # Most common errors
        error_query = f"""
        SELECT 
            last_error_message,
            COUNT(*) as count,
            item_type,
            AVG(retry_count) as avg_retries
        FROM processed_items 
        WHERE {where_clause} AND last_error_message IS NOT NULL
        GROUP BY last_error_message, item_type
        ORDER BY count DESC
        LIMIT 15
        """
        
        cursor = conn.execute(error_query, params)
        common_errors = []
        for row in cursor.fetchall():
            common_errors.append({
                "error_message": row[0],
                "count": row[1],
                "item_type": row[2],
                "avg_retries": round(row[3], 1) if row[3] else 0
            })
        
        # Error trends
        error_trend_query = f"""
        SELECT 
            DATE(last_processed_at) as date,
            COUNT(CASE WHEN last_processing_status = 'failed' THEN 1 END) as error_count,
            COUNT(*) as total_count
        FROM processed_items 
        WHERE {where_clause}
        GROUP BY DATE(last_processed_at)
        ORDER BY date DESC
        LIMIT 14
        """
        
        cursor = conn.execute(error_trend_query, params)
        error_trends = []
        for row in cursor.fetchall():
            total = row[2]
            errors = row[1]
            error_trends.append({
                "date": row[0],
                "error_count": errors,
                "total_count": total,
                "error_rate": round((errors / total) * 100, 2) if total > 0 else 0
            })
        
        return {
            "common_errors": common_errors,
            "error_trends": error_trends
        }
    
    def _get_review_analysis(self, conn, where_clause: str, params: List) -> Dict[str, Any]:
        """Analyze review data patterns"""
        
        # Review score distribution
        score_query = f"""
        SELECT 
            r.source,
            COUNT(*) as count,
            AVG(r.score) as avg_score,
            MIN(r.score) as min_score,
            MAX(r.score) as max_score
        FROM item_reviews r
        JOIN processed_items p ON r.processed_item_id = p.id
        WHERE {where_clause.replace('last_processed_at', 'p.last_processed_at')}
        GROUP BY r.source
        ORDER BY count DESC
        """
        
        cursor = conn.execute(score_query, params)
        by_source = []
        for row in cursor.fetchall():
            by_source.append({
                "source": row[0],
                "count": row[1],
                "avg_score": round(row[2], 2) if row[2] else 0,
                "min_score": round(row[3], 2) if row[3] else 0,
                "max_score": round(row[4], 2) if row[4] else 0
            })
        
        # Items with most reviews
        most_reviewed_query = f"""
        SELECT 
            p.title,
            p.item_type,
            COUNT(r.id) as review_count,
            AVG(r.score) as avg_score
        FROM processed_items p
        LEFT JOIN item_reviews r ON p.id = r.processed_item_id
        WHERE {where_clause}
        GROUP BY p.id, p.title, p.item_type
        HAVING review_count > 0
        ORDER BY review_count DESC, avg_score DESC
        LIMIT 10
        """
        
        cursor = conn.execute(most_reviewed_query, params)
        most_reviewed = []
        for row in cursor.fetchall():
            most_reviewed.append({
                "title": row[0],
                "item_type": row[1],
                "review_count": row[2],
                "avg_score": round(row[3], 2) if row[3] else 0
            })
        
        return {
            "by_source": by_source,
            "most_reviewed_items": most_reviewed
        }
    
    def _get_trend_analysis(self, conn, where_clause: str, params: List, days_back: int) -> Dict[str, Any]:
        """Analyze processing trends over time"""
        
        # Daily processing volume
        daily_query = f"""
        SELECT 
            DATE(last_processed_at) as date,
            COUNT(*) as items_processed,
            COUNT(CASE WHEN last_processing_status = 'success' THEN 1 END) as successful,
            AVG(last_processing_duration) as avg_duration
        FROM processed_items 
        WHERE {where_clause}
        GROUP BY DATE(last_processed_at)
        ORDER BY date DESC
        LIMIT {min(days_back, 30)}
        """
        
        cursor = conn.execute(daily_query, params)
        daily_volume = []
        for row in cursor.fetchall():
            total = row[1]
            successful = row[2]
            daily_volume.append({
                "date": row[0],
                "items_processed": total,
                "successful": successful,
                "success_rate": round((successful / total) * 100, 2) if total > 0 else 0,
                "avg_duration": round(row[3], 2) if row[3] else 0
            })
        
        return {
            "daily_volume": daily_volume
        }
    
    def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on report data"""
        recommendations = []
        
        summary = report.get("summary", {})
        performance = report.get("performance", {})
        errors = report.get("errors", {})
        
        # Success rate recommendations
        success_rate = summary.get("success_rate", 0)
        if success_rate < 90:
            recommendations.append(f"Success rate is {success_rate}% - consider investigating common errors")
        elif success_rate > 95:
            recommendations.append("Excellent success rate! Consider increasing processing volume")
        
        # Performance recommendations
        avg_time = summary.get("avg_processing_time", 0)
        if avg_time > 30:
            recommendations.append(f"Average processing time is {avg_time}s - consider optimization")
        
        # Error recommendations
        common_errors = errors.get("common_errors", [])
        if common_errors:
            top_error = common_errors[0]
            recommendations.append(f"Most common error: '{top_error['error_message'][:50]}...' - affects {top_error['count']} items")
        
        # Performance by type recommendations
        by_type = performance.get("by_item_type", [])
        if by_type:
            slowest_type = by_type[0]
            if slowest_type["avg_time"] > 45:
                recommendations.append(f"{slowest_type['item_type']} items are slowest (avg {slowest_type['avg_time']}s) - consider type-specific optimization")
        
        if not recommendations:
            recommendations.append("Processing is running smoothly! No specific issues detected.")
        
        return recommendations
    
    def export_processing_data(self, format: str = 'csv', library_id: Optional[str] = None, 
                             days_back: int = 30) -> str:
        """
        Export processing data for external analysis
        
        Args:
            format: Export format ('csv', 'json')
            library_id: Filter by library ID
            days_back: Number of days to export
            
        Returns:
            Path to exported file
        """
        conn = self._get_connection()
        
        try:
            # Date filter
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            where_conditions = ["last_processed_at >= ?"]
            params = [cutoff_date.isoformat()]
            
            if library_id:
                where_conditions.append("jellyfin_library_id = ?")
                params.append(library_id)
            
            where_clause = " AND ".join(where_conditions)
            
            # Export query
            query = f"""
            SELECT 
                jellyfin_item_id,
                jellyfin_library_id,
                item_type,
                title,
                year,
                last_processing_status,
                last_processing_duration,
                last_processed_at,
                processing_count,
                last_error_message,
                badges_applied,
                highest_review_score,
                lowest_review_score
            FROM processed_items 
            WHERE {where_clause}
            ORDER BY last_processed_at DESC
            """
            
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            lib_suffix = f"_lib_{library_id}" if library_id else ""
            filename = f"aphrodite_export_{timestamp}{lib_suffix}.{format}"
            filepath = os.path.join("data", filename)
            
            # Ensure data directory exists
            os.makedirs("data", exist_ok=True)
            
            if format.lower() == 'csv':
                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    # Write header
                    writer.writerow([
                        'jellyfin_item_id', 'jellyfin_library_id', 'item_type', 'title', 'year',
                        'last_processing_status', 'last_processing_duration', 'last_processed_at',
                        'processing_count', 'last_error_message', 'badges_applied',
                        'highest_review_score', 'lowest_review_score'
                    ])
                    # Write data
                    writer.writerows(rows)
            
            elif format.lower() == 'json':
                data = []
                columns = [
                    'jellyfin_item_id', 'jellyfin_library_id', 'item_type', 'title', 'year',
                    'last_processing_status', 'last_processing_duration', 'last_processed_at',
                    'processing_count', 'last_error_message', 'badges_applied',
                    'highest_review_score', 'lowest_review_score'
                ]
                
                for row in rows:
                    item = dict(zip(columns, row))
                    # Parse JSON fields
                    if item['badges_applied']:
                        try:
                            item['badges_applied'] = json.loads(item['badges_applied'])
                        except:
                            pass
                    data.append(item)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump({
                        "exported_at": datetime.now().isoformat(),
                        "period_days": days_back,
                        "library_filter": library_id,
                        "total_items": len(data),
                        "data": data
                    }, f, indent=2, default=str)
            
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            return filepath
            
        finally:
            conn.close()
    
    def get_processing_statistics_summary(self, library_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get quick processing statistics summary
        
        Args:
            library_id: Filter by library ID
            
        Returns:
            Summary statistics
        """
        conn = self._get_connection()
        
        try:
            where_conditions = []
            params = []
            
            if library_id:
                where_conditions.append("jellyfin_library_id = ?")
                params.append(library_id)
            
            where_clause = " WHERE " + " AND ".join(where_conditions) if where_conditions else ""
            
            # Basic stats
            query = f"""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN last_processing_status = 'success' THEN 1 END) as successful,
                COUNT(CASE WHEN last_processing_status = 'failed' THEN 1 END) as failed,
                AVG(last_processing_duration) as avg_duration,
                COUNT(CASE WHEN last_processed_at >= datetime('now', '-24 hours') THEN 1 END) as last_24h,
                COUNT(CASE WHEN last_processed_at >= datetime('now', '-7 days') THEN 1 END) as last_7d
            FROM processed_items {where_clause}
            """
            
            cursor = conn.execute(query, params)
            row = cursor.fetchone()
            
            if not row or row[0] == 0:
                return {"total": 0, "message": "No processed items found"}
            
            total = row[0]
            successful = row[1] or 0
            failed = row[2] or 0
            
            return {
                "total_items": total,
                "successful": successful,
                "failed": failed,
                "success_rate": round((successful / total) * 100, 2) if total > 0 else 0,
                "avg_processing_time": round(row[3] or 0, 2),
                "processed_last_24h": row[4] or 0,
                "processed_last_7d": row[5] or 0
            }
            
        finally:
            conn.close()
