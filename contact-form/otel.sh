#!/bin/bash

# OpenTelemetry Configuration
export OTEL_RESOURCE_ATTRIBUTES="service.name=contact-form,service.version=1.0.0"
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
export OTEL_EXPORTER_OTLP_PROTOCOL=grpc
export OTEL_EXPORTER_OTLP_INSECURE=true


export SENDGRID_API_KEY=
export SENDGRID_FROM_EMAIL=prabhdeepsinghgill1@gmail.com
export SENDGRID_TO_EMAIL=prabhdeepsinghgill1@gmail.com



# Start the FastAPI app with instrumentation enabled
echo "Starting Contact Form with OpenTelemetry enabled..."
python3 -m uvicorn app:app --host 0.0.0.0 --port 8001

