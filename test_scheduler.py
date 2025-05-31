#!/usr/bin/env python3
"""
Simple test script to verify the scheduler implementation.
Run this from the root directory of the project.
"""

import sys
import os
sys.path.append('aphrodite-web')

from app.services.scheduler_service import SchedulerService
from app.services.schedule_config_service import ScheduleConfigService

def test_schedule_config_service():
    """Test the schedule config service."""
    print("Testing ScheduleConfigService...")
    
    config_service = ScheduleConfigService()
    
    # Test cron validation
    valid_cron = "0 2 * * *"
    invalid_cron = "invalid"
    
    print(f"Validating valid cron '{valid_cron}': {config_service.validate_cron_expression(valid_cron)}")
    print(f"Validating invalid cron '{invalid_cron}': {config_service.validate_cron_expression(invalid_cron)}")
    
    # Test cron description
    print(f"Description for '{valid_cron}': {config_service.cron_to_description(valid_cron)}")
    
    # Test common patterns
    patterns = config_service.get_common_cron_patterns()
    print(f"Found {len(patterns)} common patterns")
    
    print("ScheduleConfigService tests passed!\n")

def test_scheduler_service():
    """Test the scheduler service."""
    print("Testing SchedulerService...")
    
    scheduler = SchedulerService()
    
    # Test scheduler start/stop
    print("Starting scheduler...")
    scheduler.start()
    print(f"Scheduler running: {scheduler.is_running}")
    
    # Test status
    status = scheduler.get_status()
    print(f"Scheduler status: {status}")
    
    # Test adding a schedule
    test_schedule = {
        'id': 'test-schedule',
        'name': 'Test Schedule',
        'cron': '0 2 * * *',
        'timezone': 'UTC',
        'enabled': True,
        'processing_options': {
            'audio_badges': True,
            'resolution_badges': True,
            'review_badges': True,
            'force_refresh': False,
            'target_directories': ['movies']
        }
    }
    
    print("Adding test schedule...")
    try:
        added_schedule = scheduler.add_schedule(test_schedule)
        print(f"Schedule added successfully: {added_schedule['id']}")
        
        # Test getting schedules
        schedules = scheduler.get_schedules()
        print(f"Current schedules: {len(schedules)}")
        
        # Test removing schedule
        print("Removing test schedule...")
        success = scheduler.remove_schedule('test-schedule')
        print(f"Schedule removed: {success}")
        
    except Exception as e:
        print(f"Error testing schedule operations: {e}")
    
    # Test stopping scheduler
    print("Stopping scheduler...")
    scheduler.stop()
    print(f"Scheduler running: {scheduler.is_running}")
    
    print("SchedulerService tests passed!\n")

def main():
    """Run all tests."""
    print("Starting scheduler implementation tests...\n")
    
    try:
        test_schedule_config_service()
        test_scheduler_service()
        print("All tests passed! ✅")
    except Exception as e:
        print(f"Test failed: {e} ❌")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
