from sanic import Sanic
from sanic.response import json

app = Sanic(name="otel-sanic")

@app.route('/')
async def test(request):
    return json({'hello': 'world'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,auto_reload=True)