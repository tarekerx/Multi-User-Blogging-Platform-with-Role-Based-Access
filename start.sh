#!/bin/bash
#!/bin/bash
#!/bin/bash
flask db init
flask db migrate -m "Initial"
flask db upgrade


echo "🚀 Starting Gunicorn"
gunicorn app:app