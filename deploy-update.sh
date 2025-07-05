#!/bin/bash

set -e  # Exit immediately if a command fails
FUNCTION_NAME="rain_alert_lambda"
BUILD_DIR="build"
ZIP_FILE="function.zip"

echo "🚧 Cleaning old build..."
rm -rf $BUILD_DIR $ZIP_FILE

echo "📦 Creating build directory..."
mkdir -p $BUILD_DIR

echo "📥 Installing dependencies (requests)..."
pip3 install requests -t $BUILD_DIR

echo "📄 Copying source files..."
cp lambda_function.py config.json $BUILD_DIR/

echo "🗜️  Zipping package..."
cd $BUILD_DIR
zip -r ../$ZIP_FILE .
cd ..

echo "🚀 Deploying to AWS Lambda..."
aws lambda update-function-code \
  --function-name $FUNCTION_NAME \
  --zip-file fileb://$ZIP_FILE

echo "✅ Deployment complete."

