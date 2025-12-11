#!/bin/bash
# Quick setup script for MongoDB connection

echo "Creating .env file..."

cat > .env << EOF
MONGODB_URI=mongodb+srv://alighazi0609:Testing12345@citydata.drepwxn.mongodb.net/smartcity?retryWrites=true&w=majority
MONGODB_DB_NAME=smartcity
JWT_SECRET_KEY=dev-secret-key-change-in-production
ENV=development
DEBUG=True
API_RATE_LIMIT=100 per hour
CORS_ORIGINS=*
EOF

echo "✅ .env file created!"
echo ""
echo "Next steps:"
echo "1. Test connection: python3 -c \"from database import Database; Database.connect(); print('✅ Connected!')\""
echo "2. Seed database: python3 seed_data.py"
echo "3. Start server: python3 app.py"

