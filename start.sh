#!/bin/bash
#!/bin/bash
#!/bin/bash
flask init-db
echo "🔧 Running flask init-db..."
flask init-db

echo "🚀 Starting Gunicorn"
gunicorn app:app