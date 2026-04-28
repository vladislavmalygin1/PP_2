# In connect.py
import psycopg2
from config import load_config

def connect(config=None): # Add =None here
    """ Connect to the PostgreSQL database server """
    if config is None:
        config = load_config() # Automatically load if not provided
        
    try:
        # Note: To use 'with connect() as conn:', 
        # this function must return the connection object
        return psycopg2.connect(**config)
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)
        raise error

