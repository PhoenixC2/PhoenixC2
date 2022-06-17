from Utils.libraries import *
"""Connect to the Database"""
conn = connect("Data/db.sqlite3", check_same_thread=False)
curr = conn.cursor()
def close_db():
    """Close the Database connection"""
    curr.close()
    conn.close()
def check_db():
    """Check if the database exists and is valid"""
    try:
        curr.execute("SELECT * FROM Devices")
        curr.fetchall()
    except:
        raise Exception("Database isnt configured.")

def get_device(id: str) -> any:
    """
    Get a Device from the Database
    :param id: The ID of the Device
    :return: The Device
    """
    curr.execute("SELECT * FROM Devices WHERE id = ?", (id,))
    device = curr.fetchone()
    if not device:
        raise Exception(f"Device with ID {id} does not exist")
    return device
