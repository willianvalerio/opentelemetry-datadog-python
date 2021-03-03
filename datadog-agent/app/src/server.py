from sanic import Sanic
from sanic.response import json

from opentelemetry import trace,baggage
from opentelemetry.exporter.otlp.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchExportSpanProcessor
import os

service_name = os.getenv('DD_SERVICE')
otel_collector = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT')
app = Sanic(name=service_name)

resource = Resource.create({"service.name": service_name})

trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)
otlp_exporter = OTLPSpanExporter(endpoint=otel_collector, insecure=True)
span_processor = BatchExportSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

@app.route('/')
async def test(request):
    with tracer.start_as_current_span("hello-world"):
        return json({'hello': 'world'})

if __name__ == '__main__':
    with tracer.start_as_current_span("start"):
        print("Hello world!")
    app.run(host='0.0.0.0', port=5000,auto_reload=True)