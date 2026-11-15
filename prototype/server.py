from http.server import BaseHTTPRequestHandler,HTTPServer
from pathlib import Path
import json, webbrowser
from engine import analyze, read_csv
ROOT=Path(__file__).parent
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        names={'/':('index.html','text/html; charset=utf-8'),'/demo.csv':('demo.csv','text/csv; charset=utf-8')}
        if self.path not in names: self.send_error(404); return
        name,mime=names[self.path]; data=(ROOT/name).read_bytes()
        self.send_response(200);self.send_header('Content-Type',mime);self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
    def do_POST(self):
        if self.path!='/analyze': self.send_error(404); return
        try:
            size=int(self.headers.get('Content-Length',0))
            if size<1 or size>5000000: raise ValueError('Размер файла должен быть от 1 байта до 5 МБ')
            result=analyze(read_csv(self.rfile.read(size).decode('utf-8-sig')));code=200
        except (ValueError,UnicodeError) as e: result={'error':str(e)};code=400
        data=json.dumps(result,ensure_ascii=False).encode();self.send_response(code);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
if __name__=='__main__':
    print('Откройте http://127.0.0.1:8765  Для остановки нажмите Ctrl+C')
    webbrowser.open('http://127.0.0.1:8765')
    HTTPServer(('127.0.0.1',8765),Handler).serve_forever()
