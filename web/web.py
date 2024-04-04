import socket
from flask import Flask, request, jsonify, render_template, url_for
from parrot import Parrot

class ParrotWeb(Parrot):
    def __init__(self):
        super().__init__()
        self.app = Flask(__name__)
        self.server_ip = self.get_server_ip()
        self.setup_routes()
    
    def get_server_ip(self):
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
        @self.app.route('/')
        def index():
            return render_template('index.html', callsign=self.callsign, server_ip=self.server_ip)
        
        @self.app.route('/read_log', methods=['GET'])
        def read_log():
            lines = request.args.get('lines', None)
            filter = request.args.get('filter', None)
            log_lines = self.read_log(lines=int(lines), filter=filter)
            return jsonify(log_lines)
        
    def run(self):
        self.app.run(host=self.host, port=self.web_port, debug=self.debug)
        
if __name__ == '__main__':
    p = ParrotWeb()
    p.run()