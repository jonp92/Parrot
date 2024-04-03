import asyncio
from starlette.responses import StreamingResponse
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from parrot import Parrot

class ParrotAPI(Parrot):
    def __init__(self):
        super().__init__()
        self.app = FastAPI()
        self.origins = ["http://localhost:8000"]
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self.app.add_api_route('/read_log', self.read_log)
        self.app.add_api_route('/watch_log', self.watch_log)
    
    
    async def watch_log(self, request: Request, interval: int = 1):
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
        import uvicorn
        uvicorn.run(self.app, host=self.host, port=self.api_port)
        
if __name__ == '__main__':
    p = ParrotAPI()
    p.run()