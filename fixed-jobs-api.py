from flask import Blueprint, jsonify, request
import os
import sqlite3
import json
import logging
import traceback
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

bp = Blueprint('jobs', __name__, url_prefix='/api/jobs')

# Ensure the data directory exists
data_dir = '/app/data'
os.makedirs(data_dir, exist_ok=True)

# Database path
db_path = os.path.join(data_dir, 'jobs.db')

def init_db():
    """Initialize the jobs database if it doesn't exist."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create jobs table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            options TEXT NOT NULL,
            status TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT,
            result TEXT,
            created_at TEXT NOT NULL
        )
        ''')
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {db_path}")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        logger.error(traceback.format_exc())

# Initialize the database when this module is imported
init_db()

@bp.route('/', methods=['GET'])
def get_jobs():
    """Get a list of all jobs with pagination."""
    try:
        # Parse pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Calculate offset
        offset = (page - 1) * per_page
        
        # Connect to the database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get total count
        cursor.execute("SELECT COUNT(*) as count FROM jobs")
        total = cursor.fetchone()['count']
        
        # Get jobs for the current page
        cursor.execute(
            "SELECT * FROM jobs ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (per_page, offset)
        )
        
        # Convert rows to dictionaries
        jobs = []
        for row in cursor.fetchall():
            job = dict(row)
            if job.get('options'):
                job['options'] = json.loads(job['options'])
            if job.get('result'):
                job['result'] = json.loads(job['result'])
            jobs.append(job)
        
        # Calculate total pages
        total_pages = (total + per_page - 1) // per_page if total > 0 else 0
        
        conn.close()
        
        return jsonify({
            'success': True,
            'jobs': jobs,
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': total_pages
        })
    except Exception as e:
        logger.error(f"Error getting jobs: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/stats', methods=['GET'])
def get_job_stats():
    """Get job statistics."""
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get total job count
        cursor.execute("SELECT COUNT(*) as count FROM jobs")
        total = cursor.fetchone()['count']
        
        # Get counts by status
        cursor.execute("""
            SELECT status, COUNT(*) as count 
            FROM jobs 
            GROUP BY status
        """)
        status_counts = {row['status']: row['count'] for row in cursor.fetchall()}
        
        # Get counts by type
        cursor.execute("""
            SELECT type, COUNT(*) as count 
            FROM jobs 
            GROUP BY type
        """)
        type_counts = {row['type']: row['count'] for row in cursor.fetchall()}
        
        # Get recent jobs
        cursor.execute("""
            SELECT * FROM jobs 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        recent_jobs = []
        for row in cursor.fetchall():
            job = dict(row)
            if job.get('options'):
                job['options'] = json.loads(job['options'])
            if job.get('result'):
                job['result'] = json.loads(job['result'])
            recent_jobs.append(job)
        
        conn.close()
        
        # Initialize an empty SQLite database if none exists
        if total == 0:
            return jsonify({
                'success': True,
                'total': 0,
                'status_counts': {},
                'type_counts': {},
                'recent_jobs': []
            })
        
        return jsonify({
            'success': True,
            'total': total,
            'status_counts': status_counts,
            'type_counts': type_counts,
            'recent_jobs': recent_jobs
        })
    except Exception as e:
        logger.error(f"Error getting job stats: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
