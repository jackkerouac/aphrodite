"""
Extended Database Analytics API for Phase B
Provides additional endpoints for the comprehensive database analytics page.
"""

from flask import Blueprint, jsonify, request
import sqlite3
import json
from datetime import datetime, timedelta
import os

bp = Blueprint('database_analytics_extended', __name__, url_prefix='/api/database')

def get_database_path():
    """Get the path to the Aphrodite database"""
    is_docker = (
        os.path.exists('/app') and 
        os.path.exists('/app/settings.yaml') and 
        os.path.exists('/.dockerenv')
    )
    
    if is_docker:
        return '/app/data/aphrodite.db'
    else:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        return os.path.join(base_dir, 'data', 'aphrodite.db')

def get_db_connection():
    """Get a database connection"""
    db_path = get_database_path()
    if not os.path.exists(db_path):
        return None
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@bp.route('/comprehensive-report', methods=['GET'])
def get_comprehensive_report():
    """Get comprehensive processing report with performance metrics and trends"""
    try:
        days = request.args.get('days', 30, type=int)
        library_id = request.args.get('library_id', None)
        
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'message': 'Database not available',
                'report': None
            })
        
        # Check if table exists
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='processed_items'"
        )
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'success': True,
                'report': {
                    'summary': {'total_items': 0, 'success_rate': 0},
                    'performance': {'avg_processing_time': 0},
                    'errors': [],
                    'reviews': {'avg_score': 0},
                    'trends': [],
                    'recommendations': []
                }
            })
        
        # Build WHERE clause for library filtering
        where_clause = f"WHERE last_processed_at > datetime('now', '-{days} days')"
        params = []
        if library_id:
            where_clause += " AND jellyfin_library_id = ?"
            params.append(library_id)
        
        # 1. Summary statistics
        cursor = conn.execute(f"""
            SELECT 
                COUNT(*) as total_items,
                SUM(CASE WHEN last_processing_status = 'success' THEN 1 ELSE 0 END) as success_items,
                SUM(CASE WHEN last_processing_status = 'failed' THEN 1 ELSE 0 END) as failed_items,
                SUM(CASE WHEN last_processing_status = 'partial_success' THEN 1 ELSE 0 END) as partial_items,
                AVG(last_processing_duration) as avg_duration
            FROM processed_items {where_clause}
        """, params)
        
        summary_row = cursor.fetchone()
        total = summary_row['total_items'] or 0
        success_rate = round((summary_row['success_items'] / max(total, 1)) * 100, 1)
        
        # 2. Error analysis (top 5 most common errors)
        cursor = conn.execute(f"""
            SELECT 
                last_error_message,
                COUNT(*) as error_count
            FROM processed_items 
            {where_clause} AND last_error_message IS NOT NULL
            GROUP BY last_error_message
            ORDER BY error_count DESC
            LIMIT 5
        """, params)
        
        error_analysis = []
        for row in cursor.fetchall():
            error_analysis.append({
                'error_message': row['last_error_message'][:100] + ('...' if len(row['last_error_message']) > 100 else ''),
                'count': row['error_count']
            })
        
        # 3. Performance by item type
        cursor = conn.execute(f"""
            SELECT 
                item_type,
                COUNT(*) as count,
                AVG(last_processing_duration) as avg_duration
            FROM processed_items 
            {where_clause} AND last_processing_duration IS NOT NULL
            GROUP BY item_type
            ORDER BY count DESC
        """, params)
        
        performance_by_type = []
        for row in cursor.fetchall():
            performance_by_type.append({
                'item_type': row['item_type'],
                'count': row['count'],
                'avg_duration': round(row['avg_duration'], 2)
            })
        
        # 4. Daily trends (last 7 days)
        cursor = conn.execute(f"""
            SELECT 
                DATE(last_processed_at) as process_date,
                COUNT(*) as total_items,
                SUM(CASE WHEN last_processing_status = 'success' THEN 1 ELSE 0 END) as success_items
            FROM processed_items 
            WHERE last_processed_at > datetime('now', '-7 days')
            GROUP BY DATE(last_processed_at)
            ORDER BY process_date ASC
        """)
        
        trends = []
        for row in cursor.fetchall():
            trends.append({
                'date': row['process_date'],
                'total_items': row['total_items'],
                'success_items': row['success_items'],
                'success_rate': round((row['success_items'] / row['total_items']) * 100, 1)
            })
        
        # 5. Generate smart recommendations
        recommendations = []
        if success_rate < 80:
            recommendations.append({
                'type': 'warning',
                'title': 'Low Success Rate',
                'message': f'Success rate ({success_rate}%) is below optimal. Review error patterns.'
            })
        
        if len(error_analysis) > 0:
            recommendations.append({
                'type': 'warning', 
                'title': 'Common Errors Detected',
                'message': f'Most common error: "{error_analysis[0]["error_message"]}" ({error_analysis[0]["count"]} occurrences)'
            })
        
        report = {
            'summary': {
                'total_items': total,
                'success_items': summary_row['success_items'] or 0,
                'failed_items': summary_row['failed_items'] or 0,
                'partial_items': summary_row['partial_items'] or 0,
                'success_rate': success_rate,
                'period_days': days
            },
            'performance': {
                'avg_processing_time': round(summary_row['avg_duration'], 2) if summary_row['avg_duration'] else 0,
                'by_type': performance_by_type
            },
            'errors': error_analysis,
            'trends': trends,
            'recommendations': recommendations
        }
        
        conn.close()
        
        return jsonify({
            'success': True,
            'report': report
        })
        
    except Exception as e:
        if 'conn' in locals():
            conn.close()
        return jsonify({
            'success': False,
            'message': f'Error generating comprehensive report: {str(e)}',
            'report': None
        }), 500

@bp.route('/processed-items', methods=['GET'])
def get_processed_items():
    """Get paginated list of processed items with filtering and search"""
    try:
        # Query parameters
        page = request.args.get('page', 1, type=int)
        limit = min(request.args.get('limit', 20, type=int), 100)  # Cap at 100
        search = request.args.get('search', '').strip()
        status_filter = request.args.get('status', '')
        library_filter = request.args.get('library', '')
        
        offset = (page - 1) * limit
        
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'message': 'Database not available',
                'items': [],
                'total': 0,
                'page': page,
                'pages': 0
            })
        
        # Check if table exists
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='processed_items'"
        )
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'success': True,
                'items': [],
                'total': 0,
                'page': page,
                'pages': 0
            })
        
        # Build WHERE clause
        where_conditions = []
        params = []
        
        if search:
            where_conditions.append("title LIKE ?")
            params.append(f"%{search}%")
        
        if status_filter:
            where_conditions.append("last_processing_status = ?")
            params.append(status_filter)
        
        if library_filter:
            where_conditions.append("jellyfin_library_id = ?")
            params.append(library_filter)
        
        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)
        
        # Get total count
        count_query = f"SELECT COUNT(*) as total FROM processed_items {where_clause}"
        cursor = conn.execute(count_query, params)
        total = cursor.fetchone()['total']
        
        # Get items
        items_query = f"""
            SELECT 
                id,
                jellyfin_item_id,
                jellyfin_library_id,
                title,
                year,
                item_type,
                last_processing_status,
                last_processed_at,
                processing_count,
                last_processing_duration,
                highest_review_score
            FROM processed_items 
            {where_clause}
            ORDER BY last_processed_at DESC
            LIMIT ? OFFSET ?
        """
        
        cursor = conn.execute(items_query, params + [limit, offset])
        
        items = []
        for row in cursor.fetchall():
            items.append({
                'id': row['id'],
                'jellyfin_item_id': row['jellyfin_item_id'],
                'jellyfin_library_id': row['jellyfin_library_id'],
                'title': row['title'],
                'year': row['year'],
                'item_type': row['item_type'],
                'status': row['last_processing_status'],
                'last_processed_at': row['last_processed_at'],
                'processing_count': row['processing_count'],
                'duration': row['last_processing_duration'],
                'review_score': row['highest_review_score']
            })
        
        pages = (total + limit - 1) // limit
        
        conn.close()
        
        return jsonify({
            'success': True,
            'items': items,
            'total': total,
            'page': page,
            'pages': pages,
            'limit': limit
        })
        
    except Exception as e:
        if 'conn' in locals():
            conn.close()
        return jsonify({
            'success': False,
            'message': f'Error retrieving processed items: {str(e)}',
            'items': [],
            'total': 0,
            'page': page,
            'pages': 0
        }), 500

@bp.route('/libraries', methods=['GET'])
def get_libraries():
    """Get list of libraries with basic statistics"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'message': 'Database not available',
                'libraries': []
            })
        
        # Check if table exists
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='processed_items'"
        )
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'success': True,
                'libraries': []
            })
        
        cursor = conn.execute("""
            SELECT 
                jellyfin_library_id,
                COUNT(*) as total_items,
                SUM(CASE WHEN last_processing_status = 'success' THEN 1 ELSE 0 END) as success_items
            FROM processed_items 
            GROUP BY jellyfin_library_id
            ORDER BY total_items DESC
        """)
        
        libraries = []
        for row in cursor.fetchall():
            success_rate = round((row['success_items'] / row['total_items']) * 100, 1) if row['total_items'] > 0 else 0
            libraries.append({
                'library_id': row['jellyfin_library_id'],
                'total_items': row['total_items'],
                'success_items': row['success_items'],
                'success_rate': success_rate
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'libraries': libraries
        })
        
    except Exception as e:
        if 'conn' in locals():
            conn.close()
        return jsonify({
            'success': False,
            'message': f'Error retrieving libraries: {str(e)}',
            'libraries': []
        }), 500
