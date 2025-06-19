#!/bin/bash
flask init-db
gunicorn app:app