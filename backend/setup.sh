#!/bin/bash

# SafeNest Setup Script
echo "🚀 SafeNest Backend Setup"
echo "=========================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your OPENAI_API_KEY before continuing!"
    echo "   You can get one from: https://platform.openai.com/api-keys"
    read -p "Press enter to continue after editing .env..."
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create directories
echo "📁 Creating necessary directories..."
mkdir -p logs media staticfiles

echo ""
echo "✨ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Start Docker services: docker-compose up -d"
echo "2. Run migrations: python manage.py migrate"
echo "3. Create superuser: python manage.py createsuperuser"
echo "4. Start server: python manage.py runserver"
echo ""
echo "Or use Docker only: docker-compose up"
