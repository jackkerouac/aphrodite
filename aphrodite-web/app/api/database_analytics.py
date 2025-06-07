"""
Database Analytics API
Provides endpoints for database statistics and insights for the Aphrodite dashboard.
"""

from flask import Blueprint, jsonify, request
import sqlite3
import json
from datetime import datetime, timedelta
import os

bp = Blueprint('database_analytics', __name__, url_prefix='/api/database')

def get_database_path():
    """Get the path to the Aphrodite database"""
    # Use the same logic as other parts of the app to find the database
    is_docker = (
        os.path.exists('/app') and 
        os.path.exists('/app/settings.yaml') and 
        os.path.exists('/.dockerenv')
    )
    
    if is_docker:
        return '/app/data/aphrodite.db'
    else:
        # For local development - go up from app/api to root
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        return os.path.join(base_dir, 'data', 'aphrodite.db')

def get_db_connection():
    """Get a database connection"""
    db_path = get_database_path()
    if not os.path.exists(db_path):
        return None
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    return conn

@bp.route('/stats', methods=['GET'])
def get_database_stats():
    """Get comprehensive database statistics for the dashboard"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'message': 'Database not available',
                'stats': None
            })
        
        # Check if processed_items table exists
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='processed_items'"
        )
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'success': True,
                'message': 'Database tracking not yet initialized',
                'stats': {
                    'total_items': 0,
                    'success_rate': 0,
                    'recent_activity': {
                        'last_24h': 0,
                        'last_7d': 0,
                        'last_30d': 0
                    },
                    'status_breakdown': {},
                    'performance_metrics': {
                        'avg_processing_time': 0
                    },
                    'review_insights': {
                        'items_with_reviews': 0,
                        'avg_review_score': 0
                    }
                }
            })
        
        stats = {}
        
        # 1. Total items and status breakdown
        cursor = conn.execute("""
            SELECT 
                COUNT(*) as total_items,
                last_processing_status,
                COUNT(*) as status_count
            FROM processed_items 
            GROUP BY last_processing_status
        """)
        
        status_breakdown = {}
        total_items = 0
        
        for row in cursor.fetchall():
            if row['last_processing_status']:
                status_breakdown[row['last_processing_status']] = row['status_count']
                total_items += row['status_count']
        
        # If no status breakdown, get total count
        if total_items == 0:
            cursor = conn.execute("SELECT COUNT(*) as total FROM processed_items")
            result = cursor.fetchone()
            total_items = result['total'] if result else 0
        
        stats['total_items'] = total_items
        stats['status_breakdown'] = status_breakdown
        
        # 2. Success rate
        success_count = status_breakdown.get('success', 0)
        stats['success_rate'] = round((success_count / max(total_items, 1)) * 100, 1)
        
        # 3. Recent activity (24h, 7d, 30d)
        now = datetime.now()
        
        # 24 hours ago
        time_24h = (now - timedelta(hours=24)).isoformat()
        cursor = conn.execute(
            "SELECT COUNT(*) as count FROM processed_items WHERE last_processed_at > ?",
            (time_24h,)
        )
        activity_24h = cursor.fetchone()['count']
        
        # 7 days ago
        time_7d = (now - timedelta(days=7)).isoformat()
        cursor = conn.execute(
            "SELECT COUNT(*) as count FROM processed_items WHERE last_processed_at > ?",
            (time_7d,)
        )
        activity_7d = cursor.fetchone()['count']
        
        # 30 days ago
        time_30d = (now - timedelta(days=30)).isoformat()
        cursor = conn.execute(
            "SELECT COUNT(*) as count FROM processed_items WHERE last_processed_at > ?",
            (time_30d,)
        )
        activity_30d = cursor.fetchone()['count']
        
        stats['recent_activity'] = {
            'last_24h': activity_24h,
            'last_7d': activity_7d,
            'last_30d': activity_30d
        }
        
        # 4. Performance metrics
        cursor = conn.execute("""
            SELECT 
                AVG(last_processing_duration) as avg_duration,
                COUNT(*) as items_with_duration
            FROM processed_items 
            WHERE last_processing_duration IS NOT NULL AND last_processing_duration > 0
        """)
        
        perf_row = cursor.fetchone()
        avg_duration = perf_row['avg_duration'] if perf_row['avg_duration'] else 0
        
        stats['performance_metrics'] = {
            'avg_processing_time': round(avg_duration, 2) if avg_duration else 0,
            'items_with_timing': perf_row['items_with_duration']
        }
        
        # 5. Review insights
        cursor = conn.execute("""
            SELECT 
                COUNT(DISTINCT p.id) as items_with_reviews,
                AVG(r.score) as avg_score,
                COUNT(r.id) as total_reviews
            FROM processed_items p
            LEFT JOIN item_reviews r ON p.id = r.processed_item_id
            WHERE r.id IS NOT NULL
        """)
        
        review_row = cursor.fetchone()
        
        stats['review_insights'] = {
            'items_with_reviews': review_row['items_with_reviews'] or 0,
            'avg_review_score': round(review_row['avg_score'], 1) if review_row['avg_score'] else 0,
            'total_reviews': review_row['total_reviews'] or 0
        }
        
        # 6. Top libraries by activity
        cursor = conn.execute("""
            SELECT 
                jellyfin_library_id,
                COUNT(*) as item_count,
                SUM(CASE WHEN last_processing_status = 'success' THEN 1 ELSE 0 END) as success_count
            FROM processed_items 
            GROUP BY jellyfin_library_id
            ORDER BY item_count DESC
            LIMIT 5
        """)
        
        top_libraries = []
        for row in cursor.fetchall():
            success_rate = round((row['success_count'] / row['item_count']) * 100, 1) if row['item_count'] > 0 else 0
            top_libraries.append({
                'library_id': row['jellyfin_library_id'],
                'item_count': row['item_count'],
                'success_rate': success_rate
            })
        
        stats['top_libraries'] = top_libraries
        
        conn.close()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        if 'conn' in locals():
            conn.close()
        return jsonify({
            'success': False,
            'message': f'Error retrieving database statistics: {str(e)}',
            'stats': None
        }), 500

@bp.route('/recent-items', methods=['GET'])
def get_recent_items():
    """Get recently processed items for dashboard display"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'message': 'Database not available',
                'items': []
            })
        
        # Check if table exists
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='processed_items'"
        )
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'success': True,
                'items': []
            })
        
        cursor = conn.execute("""
            SELECT 
                jellyfin_item_id,
                title,
                item_type,
                last_processing_status,
                last_processed_at,
                last_processing_duration,
                highest_review_score
            FROM processed_items 
            ORDER BY last_processed_at DESC 
            LIMIT ?
        """, (limit,))
        
        items = []
        for row in cursor.fetchall():
            items.append({
                'jellyfin_item_id': row['jellyfin_item_id'],
                'title': row['title'],
                'item_type': row['item_type'],
                'status': row['last_processing_status'],
                'processed_at': row['last_processed_at'],
                'duration': row['last_processing_duration'],
                'review_score': row['highest_review_score']
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'items': items
        })
        
    except Exception as e:
        if 'conn' in locals():
            conn.close()
        return jsonify({
            'success': False,
            'message': f'Error retrieving recent items: {str(e)}',
            'items': []
        }), 500

@bp.route('/processing-trends', methods=['GET'])
def get_processing_trends():
    """Get processing trends for the last 7 days"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'message': 'Database not available',
                'trends': []
            })
        
        # Check if table exists
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='processed_items'"
        )
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'success': True,
                'trends': []
            })
        
        # Get daily processing counts for the last 7 days
        cursor = conn.execute("""
            SELECT 
                DATE(last_processed_at) as process_date,
                COUNT(*) as total_items,
                SUM(CASE WHEN last_processing_status = 'success' THEN 1 ELSE 0 END) as success_items,
                SUM(CASE WHEN last_processing_status = 'failed' THEN 1 ELSE 0 END) as failed_items
            FROM processed_items 
            WHERE last_processed_at > datetime('now', '-7 days')
            GROUP BY DATE(last_processed_at)
            ORDER BY process_date ASC
        """)
        
        trends = []
        for row in cursor.fetchall():
            success_rate = round((row['success_items'] / row['total_items']) * 100, 1) if row['total_items'] > 0 else 0
            trends.append({
                'date': row['process_date'],
                'total_items': row['total_items'],
                'success_items': row['success_items'],
                'failed_items': row['failed_items'],
                'success_rate': success_rate
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'trends': trends
        })
        
    except Exception as e:
        if 'conn' in locals():
            conn.close()
        return jsonify({
            'success': False,
            'message': f'Error retrieving processing trends: {str(e)}',
            'trends': []
        }), 500
