#!/bin/bash
#!/bin/bash
#!/bin/bash
flask db downgrade base
flask db stamp head  # Resync migrations without rerunning old ones
flask db migrate -m "fresh migration"
flask db upgrade


echo "🚀 Starting Gunicorn"
gunicorn app:app