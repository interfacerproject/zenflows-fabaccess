#!/bin/sh

curl -X POST -H 'Content-Type:application/json' -d "@session.json" http://localhost:8000/new-session
