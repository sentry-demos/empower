#!/bin/bash

# Start Angular development server with localhost backends
# This script starts ng serve with localhost backend URLs

echo "🚀 Starting Angular development server with localhost backends..."
echo "📋 Backend URLs:"
echo "   Flask: http://localhost:8080"
echo "   Laravel: http://localhost:8000"
echo ""

# Start the Angular development server
echo "🌐 Starting Angular dev server..."
npx ng serve
