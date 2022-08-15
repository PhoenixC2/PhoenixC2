# Reverse HTTP Listener
from Utils import *
from Handlers.http.reverse.tcp.linux import Linux
from Handlers.http.reverse.tcp.windows import Windows
from Listeners.base import Base_Listener

class Listener(Base_Listener):
    """The Reverse HTTP Listener Class"""
    def __init__(self, server, config, id):
        super().__init__(server, config, id)
    
    def refresh_connections(self):
        # Check if the connections are still alive
        while True:
            if self.stopped:
                break
            for device in self.handlers:
                if not device.alive():
                    self.remove_handler(device)
            time.sleep(1)
            

    def listen(self):
        while True:
            # Check if Server stopped
            if self.stopped:
                break
            try:
                # Accept the Connection
                connection, addr = self.listener.accept()
            except socket.timeout:
                pass
            except Exception as e:
                print(e)
            else:
                key = Fernet.generate_key()
                self.fernet = Fernet(key)
                try:
                    connection.send(key)
                except:
                    continue
                log(
                    f"New Connection established from {addr[0]}", alert="success")
                try:
                    operating_system = self.decrypt(
                        connection.recv(1024)).lower()
                except:
                    log(f"Connection to {addr[0]} has been lost.",
                        alert="critical")
                    connection.close()
                    continue
                if operating_system == "windows":
                    self.add_handler(
                        Windows(connection, addr[0], key, self.server.active_handlers_count + 1))  # Create a Windows Object to store the connection
                elif operating_system == "linux":
                    self.add_handler(
                        Linux(connection, addr[0], key, self.server.active_handlers_count + 1))  # Create a Linux Object to store the connection
                else:
                    log(f"Unknown Operating System: {operating_system}",
                        alert="error")
                    connection.close()
                    continue

    def start(self):
        ADDR = (self.address, self.port)
        try:
            self.listener.bind(ADDR)
        except:
            raise Exception("Port is already in use.")
        self.listener.listen()
        # Start the Listener and Refresher
        self.listener_thread = threading.Thread(
            target=self.listen, name="Listener " + str(self.id))
        self.listener_thread.start()

        self.refresher_thread = threading.Thread(
            target=self.refresh_connections, name="Refresher")
        self.refresher_thread.start()

    def stop(self):
        # Stop the Server
        self.stopped = True

    def status(self):
        """Get Status of the Server

        Returns:
            bool: True if socket is running, False if not
            bool: True if listener is running, False if not
            bool: True if refresher is running, False if not"""
        # Return the Status of the Listener
        return self.stopped, self.listener_thread.is_alive(), self.refresher_thread.is_alive()