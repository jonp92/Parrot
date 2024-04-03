from flask import Flask, request, jsonify, render_template, url_for
from parrot import Parrot

class ParrotWeb(Parrot):
    def __init__(self):
        super().__init__()
        self.app = Flask(__name__)
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/')
        def index():
            return render_template('index.html')
        
        @self.app.route('/read_log', methods=['GET'])
        def read_log():
            lines = request.args.get('lines', None)
            filter = request.args.get('filter', None)
            log_lines = self.read_log(lines=int(lines), filter=filter)
            return jsonify(log_lines)
        
        @self.app.route('/watch_log', methods=['GET'])
        def watch_log():
            return render_template('watch_log.html', callsign=self.callsign)
        
    def run(self):
        self.app.run(host=self.host, port=self.web_port, debug=self.debug)
        
if __name__ == '__main__':
    p = ParrotWeb()
    p.run()