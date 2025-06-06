#!/usr/bin/env python3
# aphrodite-web/app/api/review_sources.py

from flask import Blueprint, request, jsonify
import sqlite3
import json
import os
from pathlib import Path

bp = Blueprint('review_sources', __name__, url_prefix='/api')

def get_db_path():
    """Get the path to the SQLite database"""
    # Check if we're in Docker
    is_docker = os.path.exists('/.dockerenv')
    if is_docker:
        return '/app/data/aphrodite.db'
    else:
        # Find the root directory (where data folder should be)
        current_dir = Path(__file__).parent
        # Go up until we find the root aphrodite directory
        for _ in range(10):  # Safety limit
            if (current_dir / 'data').exists() or current_dir.name == 'aphrodite':
                return str(current_dir / 'data' / 'aphrodite.db')
            current_dir = current_dir.parent
        
        # Fallback
        return str(Path(__file__).parents[4] / 'data' / 'aphrodite.db')

def get_db_connection():
    """Get a database connection"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@bp.route('/review-sources', methods=['GET'])
def get_review_sources():
    """Get all review sources with their settings"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM review_sources 
            ORDER BY display_order, priority
        ''')
        
        sources = []
        for row in cursor.fetchall():
            source = dict(row)
            # Convert boolean values
            source['enabled'] = bool(source['enabled'])
            sources.append(source)
        
        conn.close()
        return jsonify(sources)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/review-sources/<int:source_id>', methods=['PUT'])
def update_review_source(source_id):
    """Update a specific review source"""
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE review_sources 
            SET enabled = ?, display_order = ?, priority = ?, max_variants = ?,
                conditions = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            data.get('enabled', False),
            data.get('display_order', 0),
            data.get('priority', 0),
            data.get('max_variants', 1),
            data.get('conditions'),
            source_id
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/review-sources/reorder', methods=['PUT'])
def reorder_review_sources():
    """Reorder review sources based on new priorities"""
    try:
        data = request.get_json()
        source_orders = data.get('sources', [])
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        for order, source_data in enumerate(source_orders, 1):
            cursor.execute('''
                UPDATE review_sources 
                SET display_order = ?, priority = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (order, order, source_data['id']))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/review-settings', methods=['GET'])
def get_review_settings():
    """Get review source settings"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT setting_key, setting_value FROM review_settings')
        
        settings = {}
        for row in cursor.fetchall():
            key = row['setting_key']
            value = row['setting_value']
            
            # Convert specific settings to appropriate types
            if key == 'max_badges_display':
                settings[key] = int(value)
            elif key in ['show_percentage_only', 'group_related_sources', 'anime_sources_for_anime_only']:
                settings[key] = value == '1' or value.lower() == 'true'
            else:
                settings[key] = value
        
        conn.close()
        return jsonify(settings)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/review-settings', methods=['PUT'])
def update_review_settings():
    """Update review source settings"""
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        for key, value in data.items():
            # Convert value to string for storage
            if isinstance(value, bool):
                str_value = '1' if value else '0'
            else:
                str_value = str(value)
            
            cursor.execute('''
                INSERT OR REPLACE INTO review_settings (setting_key, setting_value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (key, str_value))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/review-sources/enabled', methods=['GET'])
def get_enabled_review_sources():
    """Get only enabled review sources in priority order"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM review_sources 
            WHERE enabled = 1 
            ORDER BY priority, display_order
        ''')
        
        sources = []
        for row in cursor.fetchall():
            source = dict(row)
            source['enabled'] = bool(source['enabled'])
            sources.append(source)
        
        conn.close()
        return jsonify(sources)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
