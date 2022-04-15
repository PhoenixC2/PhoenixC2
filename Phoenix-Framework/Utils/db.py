from Utils.libraries import *
conn = connect("Data/db.sqlite3")
curr = conn.cursor()

def get_listeners():
    """Return all Listeners from the Database"""
    curr.execute("SELECT * FROM Listeners")
    return curr.fetchall()
def get_devices():
    """Return all Devices from the Database"""
    curr.execute("SELECT * FROM Devices")
    return curr.fetchall()
def get_stagers():
    """Return all Stagers from the Database"""
    curr.execute("SELECT * FROM Stagers")
    return curr.fetchall()
def check_db():
    """Check if the database exists and is valid"""
    try:
        curr.execute("SELECT * FROM Devices")
        curr.fetchall()
    except:
        raise Exception("Database isnt configured.")