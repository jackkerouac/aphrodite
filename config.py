import os

class Config:
    # Base directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Database
    DATABASE_URI = os.path.join(BASE_DIR, 'data', 'aphrodite.db')
    
    # Aphrodite script path
    APHRODITE_SCRIPT_PATH = os.path.abspath(os.path.join(BASE_DIR, '..', 'aphrodite-python', 'aphrodite.py'))
    
    # Configuration files
    CONFIG_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'aphrodite-python'))
    
    # Image directories
    ORIGINAL_POSTERS_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'aphrodite-python', 'posters', 'original'))
    MODIFIED_POSTERS_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'aphrodite-python', 'posters', 'modified'))
    WORKING_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'aphrodite-python', 'posters', 'working'))