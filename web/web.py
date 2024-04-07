import socket
from flask import Flask, request, jsonify, render_template, url_for
from flask_compress import Compress
from parrot import Parrot

'''
ParrotWeb is a class that extends Parrot and adds a web interface to the Parrot application.

ParrotWeb is reliant on ParrotAPI to be running on port 8001 to provide the API for the web interface.
ParrotAPI is responsible for using the Parrot class to read the desired log file and serve the log lines using FastAPI.
ParrotWeb receives data from ParrotAPI utilizing SSE (Server-Sent Events) to update the Radio Display and log table in real-time.

Attributes:
    app: A Flask object that represents the web application
    server_ip: A string that represents the IP address of the server

Methods:
    get_server_ip: A method that gets the IP address of the server
    setup_routes: A method that sets up the routes for the web application
    run: A method that runs the web application

Returns:
    None
'''
class ParrotWeb(Parrot):
    def __init__(self):
        super().__init__()
        self.app = Flask(__name__)
        Compress(self.app)
        self.server_ip = self.get_server_ip()
        self.setup_routes()
    
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

    def setup_routes(self):
        '''
        setup_routes is a method that sets up the routes for the web application.
        
        Parameters:
            None
            
        Returns:
            None
        '''
        @self.app.route('/')
        def index():
            '''
            index is a route that renders the index.html template.
            
            Parameters:
                None
                
            Returns:
                render_template: A Flask function that renders the index.html template
            '''
            return render_template('index.html', callsign=self.callsign, server_ip=self.server_ip)
        
        @self.app.route('/read_log', methods=['GET'])
        def read_log():
            '''
            read_log is a route that reads the log file and returns the log lines.
            
            Parameters:
                None
            
            Returns:
                jsonify: A Flask function that returns the log lines as a JSON object
            '''
            lines = request.args.get('lines', None)
            filter = request.args.get('filter', None)
            log_lines = self.read_log(lines=int(lines), filter=filter)
            return jsonify(log_lines)
        
    def run(self):
        '''
        run is a method that runs the web application.
        
        This method runs the web application on the specified host and port.
        self.host, self.web_port, and self.debug are set in the config.json file for the Parrot application.
        '''
        self.app.run(host=self.host, port=self.web_port, debug=self.debug)
        
if __name__ == '__main__':
    '''
    main is the entry point for the ParrotWeb application.
    
    This code block creates an instance of ParrotWeb and runs the web application when the script is executed directly instead of being imported.
    '''
    p = ParrotWeb()
    print(f'Starting ParrotWeb on http://{p.host}:{p.web_port}')
    p.run()