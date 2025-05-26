import json
import os
import sqlite3
import time

class JobService:
    """
    Service for managing job records
    
    Jobs represent script execution tasks with the following structure:
    {
        "id": "unique-id",
        "type": "item|library|check",
        "command": "Command that was executed",
        "options": {}, # Original options passed to the API
        "status": "queued|running|success|failed",
        "start_time": 1234567890,
        "end_time": 1234567890,
        "result": {} # Result data
    }
    """
    
    DB_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'jobs.db')
    
    @classmethod
    def _init_db(cls):
        """Initialize the database if it doesn't exist"""
        conn = sqlite3.connect(cls.DB_FILE)
        cursor = conn.cursor()
        
        # Create jobs table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            type TEXT,
            command TEXT,
            options TEXT,
            status TEXT,
            start_time REAL,
            end_time REAL,
            result TEXT,
            created_at REAL
        )
        ''')
        
        conn.commit()
        conn.close()
    
    @classmethod
    def create_job(cls, job_data):
        """Create a new job record"""
        cls._init_db()
        
        conn = sqlite3.connect(cls.DB_FILE)
        cursor = conn.cursor()
        
        # Convert dict fields to JSON
        options_json = json.dumps(job_data.get('options', {}))
        result_json = json.dumps(job_data.get('result', {}))
        
        cursor.execute('''
        INSERT INTO jobs (id, type, command, options, status, start_time, end_time, result, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            job_data['id'],
            job_data['type'],
            job_data.get('command', ''),
            options_json,
            job_data['status'],
            job_data.get('start_time'),
            job_data.get('end_time'),
            result_json,
            time.time()
        ))
        
        conn.commit()
        conn.close()
        
        return job_data
    
    @classmethod
    def update_job(cls, job_id, update_data):
        """Update an existing job"""
        cls._init_db()
        
        conn = sqlite3.connect(cls.DB_FILE)
        cursor = conn.cursor()
        
        # Build the SQL update statement dynamically based on what fields are provided
        update_fields = []
        update_values = []
        
        for key, value in update_data.items():
            if key in ['options', 'result']:
                value = json.dumps(value)
            update_fields.append(f"{key} = ?")
            update_values.append(value)
        
        # Add job_id to the values list
        update_values.append(job_id)
        
        sql = f"UPDATE jobs SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(sql, update_values)
        
        conn.commit()
        conn.close()
        
        return True
    
    @classmethod
    def get_job(cls, job_id):
        """Get a job by ID"""
        cls._init_db()
        
        conn = sqlite3.connect(cls.DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM jobs WHERE id = ?', (job_id,))
        row = cursor.fetchone()
        
        if row:
            # Convert to dict and parse JSON fields
            job = dict(row)
            job['options'] = json.loads(job['options'])
            job['result'] = json.loads(job['result'])
            
            conn.close()
            return job
        
        conn.close()
        return None
    
    @classmethod
    def get_all_jobs(cls, limit=20, offset=0):
        """Get all jobs with pagination"""
        cls._init_db()
        
        conn = sqlite3.connect(cls.DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT * FROM jobs ORDER BY created_at DESC LIMIT ? OFFSET ?', 
            (limit, offset)
        )
        rows = cursor.fetchall()
        
        jobs = []
        for row in rows:
            # Convert to dict and parse JSON fields
            job = dict(row)
            job['options'] = json.loads(job['options'])
            job['result'] = json.loads(job['result'])
            jobs.append(job)
        
        conn.close()
        return jobs
    
    @classmethod
    def delete_job(cls, job_id):
        """Delete a job by ID"""
        cls._init_db()
        
        conn = sqlite3.connect(cls.DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM jobs WHERE id = ?', (job_id,))
        
        deleted = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return deleted
