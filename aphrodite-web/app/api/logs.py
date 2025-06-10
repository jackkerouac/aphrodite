"""
Logs API endpoint for viewing, filtering, and managing Aphrodite logs
"""

import os
import re
from datetime import datetime
from flask import Blueprint, jsonify, request
from pathlib import Path

bp = Blueprint('logs', __name__, url_prefix='/api/logs')

def get_log_path():
    """Get the path to the aphrodite.log file"""
    # Check if we're running in Docker
    if os.path.exists('/app') and os.path.exists('/.dockerenv'):
        return '/app/data/aphrodite.log'
    else:
        # Development environment - go from aphrodite-web/app to aphrodite/data
        base_dir = Path(os.path.abspath(__file__)).parents[3]  # Go up 3 levels
        return os.path.join(base_dir, 'data', 'aphrodite.log')

@bp.route('/', methods=['GET'])
def get_logs():
    """Get logs with optional filtering"""
    try:
        log_path = get_log_path()
        
        # Check if log file exists
        if not os.path.exists(log_path):
            return jsonify({
                'success': True,
                'logs': [],
                'message': 'Log file not found',
                'log_path': log_path
            })
        
        # Get query parameters for filtering
        log_level = request.args.get('level', '').upper()
        search_query = request.args.get('search', '').lower()
        limit = int(request.args.get('limit', 1000))  # Default to last 1000 lines
        
        # Read the log file
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        # Parse log entries
        logs = []
        for line_num, line in enumerate(lines[-limit:], start=max(1, len(lines) - limit + 1)):
            line = line.strip()
            if not line:
                continue
                
            # Try to parse log format: TIMESTAMP - LEVEL - MESSAGE
            log_match = re.match(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - (\w+) - (.+)$', line)
            
            if log_match:
                timestamp_str, level, message = log_match.groups()
                try:
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    timestamp = None
                    
                log_entry = {
                    'line_number': line_num,
                    'timestamp': timestamp_str if timestamp else 'Unknown',
                    'level': level,
                    'message': message,
                    'raw_line': line
                }
            else:
                # Handle non-standard log format or continuation lines
                log_entry = {
                    'line_number': line_num,
                    'timestamp': 'Unknown',
                    'level': 'UNKNOWN',
                    'message': line,
                    'raw_line': line
                }
            
            # Apply filters
            if log_level and log_entry['level'] != log_level:
                continue
                
            if search_query and search_query not in log_entry['message'].lower():
                continue
                
            logs.append(log_entry)
        
        # Get file info
        file_stats = os.stat(log_path)
        file_size = file_stats.st_size
        file_modified = datetime.fromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({
            'success': True,
            'logs': logs,
            'total_lines': len(lines),
            'filtered_lines': len(logs),
            'file_size': file_size,
            'file_modified': file_modified,
            'log_path': log_path
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error reading logs: {str(e)}',
            'logs': []
        }), 500

@bp.route('/levels', methods=['GET'])
def get_log_levels():
    """Get available log levels from the log file"""
    try:
        log_path = get_log_path()
        
        if not os.path.exists(log_path):
            return jsonify({
                'success': True,
                'levels': []
            })
        
        levels = set()
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                    
                # Extract level from log format
                log_match = re.match(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - (\w+) - (.+)$', line)
                if log_match:
                    level = log_match.group(2)
                    levels.add(level)
        
        return jsonify({
            'success': True,
            'levels': sorted(list(levels))
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error reading log levels: {str(e)}',
            'levels': []
        }), 500

@bp.route('/clear', methods=['POST'])
def clear_logs():
    """Clear the log file"""
    try:
        log_path = get_log_path()
        
        # Check if log file exists
        if not os.path.exists(log_path):
            return jsonify({
                'success': True,
                'message': 'Log file not found, nothing to clear'
            })
        
        # Clear the log file
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write('')
        
        return jsonify({
            'success': True,
            'message': 'Log file cleared successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error clearing logs: {str(e)}'
        }), 500

@bp.route('/download', methods=['GET'])
def download_logs():
    """Download the complete log file"""
    try:
        log_path = get_log_path()
        
        if not os.path.exists(log_path):
            return jsonify({
                'success': False,
                'message': 'Log file not found'
            }), 404
        
        # Read the entire log file
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        return jsonify({
            'success': True,
            'content': content,
            'filename': f'aphrodite-{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error downloading logs: {str(e)}'
        }), 500
