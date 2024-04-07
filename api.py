import asyncio
import socket
from starlette.responses import StreamingResponse
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from parrot import Parrot

'''
ParrotAPI is a class that extends Parrot and adds an API to the Parrot application.

ParrotAPI is responsible for using the Parrot class to read the desired log file and serve the log lines using FastAPI.
FastAPI was chosen for its simplicity and raw performance along with being ideal for supporting a large number of concurrent connections.
Additionally, adding a websocket to the API would be trivial if needed in the future due to FastAPI's support for websockets being built-in.
ParrotAPI provides two routes: /read_log and /watch_log. /read_log reads the log file and returns the log lines as a response.
/watch_log reads the log file and returns the log lines as a response in real-time using Server-Sent Events (SSE).

Attributes:
    app: A FastAPI object that represents the API application
    origins: A list of strings that represent the origins allowed to access the API
    
Methods:
    watch_log: A method that reads the log file and returns the log lines as a response in real-time using Server-Sent Events (SSE)
    get_server_ip: A method that gets the IP address of the server (Used for CORS to allow connections from the server)
    run: A method that runs the API application

Returns:
    None

Exceptions:
    asyncio.CancelledError: An exception that is raised when the connection is closed
    
'''

class ParrotAPI(Parrot):
    def __init__(self):
        '''
        ParrotAPI constructor that initializes the FastAPI application and sets up the routes for the API.
        
        '''
        super().__init__()
        self.app = FastAPI()
        self.server_ip = self.get_server_ip()
        self.hostname = socket.gethostname()
        self.origins = [self.server_ip, f'http://{self.server_ip}', f'http://{self.server_ip}:{self.web_port}', f'http://{self.hostname}', f'http://{self.hostname}:{self.web_port}']
        print(f'Allowed origins: {self.origins}')
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self.app.add_api_route('/read_log', self.read_log)
        self.app.add_api_route('/watch_log', self.watch_log)
    
    def get_server_ip(self):
        '''
        get_server_ip is a method that gets the IP address of the server.
        
        Parameters:
            None
            
        Variables:
            s: A socket object that represents a UDP socket
            
        Returns:
            ip: A string that represents the IP address of the server
            
        Exceptions:
            socket.error: An exception that is raised when there is an error with the socket
        '''
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            ip = s.getsockname()[0]
        except:
            ip = socket.gethostbyname(socket.gethostname())
        finally:
            s.close()
        return ip
    
    async def watch_log(self, request: Request, interval: int = .1):
        '''
        watch_log is a method that reads the log file and returns the log lines as a response in real-time using Server-Sent Events (SSE).
        
        Parameters:
            request: A Request object that represents the request
            interval: An integer that represents the interval between log reads
        
        Variables:
            log_lines: A list of strings that represent the log lines
        
        Returns:
            StreamingResponse: A StreamingResponse object that represents the log lines in real-time using Server-Sent Events (SSE)
        
        Exceptions:
            asyncio.CancelledError: An exception that is raised when the connection is closed
        '''
        async def event_stream():
            try:
                while True:
                    log_lines = self.read_log(lines=1)
                    for line in log_lines:
                        yield f"data: {line}\n\n"
                    await asyncio.sleep(interval)
            except asyncio.CancelledError:
                pass
            finally:
                print(f"Connection from {request.client.host} closed.")
        return StreamingResponse(event_stream(), media_type='text/event-stream')
        

    def run(self):
        '''
        run is a method that runs the API application.
        
        self.host and self.api_port are used to specify the host and port for the API application, inherited from the Parrot class and set in the config.json file.
        '''
        import uvicorn
        uvicorn.run(self.app, host=self.host, port=self.api_port)
        
if __name__ == '__main__':
    '''
    Main method that creates an instance of ParrotAPI and runs the API application.
    '''
    p = ParrotAPI()
    p.run()