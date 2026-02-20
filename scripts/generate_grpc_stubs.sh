#!/bin/bash
# Generate Python gRPC stubs from Artifact Storage proto files

set -e

echo "Generating gRPC stubs for Artifact Storage..."

# Create output directory
mkdir -p "app/grpc/generated"

# Generate Python code from proto files
python -m grpc_tools.protoc \
  -I"../Artifact Storage/api/proto/v1" \
  --python_out=app/grpc/generated \
  --grpc_python_out=app/grpc/generated \
  --pyi_out=app/grpc/generated \
  "../Artifact Storage/api/proto/v1/artifact.proto"

# Create __init__.py to make it a package
touch app/grpc/generated/__init__.py

echo "✅ gRPC stubs generated successfully in app/grpc/generated/"
echo ""
echo "Generated files:"
ls -la app/grpc/generated/
