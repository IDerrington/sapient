#!/bin/bash
# Script to set up proper proto directory structure for SAPIENT

echo "Setting up SAPIENT proto directory structure..."

# Create the directory structure that matches import paths
mkdir -p sapient_msg/bsi_flex_335_v2_0
mkdir -p sapient_msg/bsi_flex_335_v1_0

# Copy proto files to the correct locations
# Main proto files go in sapient_msg/bsi_flex_335_v2_0/
cp proto/*.proto sapient_msg/bsi_flex_335_v2_0/

cp proto/bsi_flex_335_v2_0/*.proto sapient_msg/bsi_flex_335_v2_0/
cp proto/bsi_flex_335_v1_0/*.proto sapient_msg/bsi_flex_335_v1_0/

# proto_options.proto goes in sapient_msg/ (one level up)
cp proto/proto_options.proto sapient_msg/

echo "Directory structure created:"
tree -L 2 sapient_msg/ 2>/dev/null || find sapient_msg/ -type f

echo ""
echo "Now you can generate Python code with:"
echo "python -m grpc_tools.protoc -I=. --python_out=src/generated sapient_msg/bsi_flex_335_v2_0/*.proto"
