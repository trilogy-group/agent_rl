#!/usr/bin/env python3
"""
Check tracking database status
"""
import sqlite3
import os

# Check the tracker database
db_path = 'backend/data/tracker.db'
print(f'Checking database at: {os.path.abspath(db_path)}')

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    try:
        # Check operations table structure
        cursor = conn.execute('PRAGMA table_info(tracked_operations)')
        columns = cursor.fetchall()
        print(f'Operations table columns: {[col[1] for col in columns]}')
        
        # Check current operation records
        cursor = conn.execute('SELECT id, operation_name, status, started_at, ended_at, input_data IS NOT NULL, output_data IS NOT NULL FROM tracked_operations ORDER BY started_at DESC LIMIT 5')
        rows = cursor.fetchall()
        
        print(f'\nFound {len(rows)} operation records:')
        for i, row in enumerate(rows):
            print(f'  {i+1}. ID: {row[0][:8]}..., Name: {row[1]}, Status: {row[2]}, Has Input: {row[5]}, Has Output: {row[6]}')
        
        # Check if we have any duplicate operations (same name + thread_id with multiple records)
        cursor = conn.execute('''
            SELECT operation_name, thread_id, COUNT(*) as count, 
                   GROUP_CONCAT(status) as statuses
            FROM tracked_operations 
            GROUP BY operation_name, thread_id 
            HAVING COUNT(*) > 1
            ORDER BY count DESC
        ''')
        duplicates = cursor.fetchall()
        
        if duplicates:
            print(f'\nFound {len(duplicates)} potential duplicate operation groups:')
            for dup in duplicates[:3]:  # Show first 3
                print(f'  {dup[0]} in thread {dup[1][:8]}... has {dup[2]} records with statuses: {dup[3]}')
        else:
            print('\n✅ No duplicate operations found - single-row tracking is working!')
            
    finally:
        conn.close()
else:
    print('❌ Database does not exist yet')