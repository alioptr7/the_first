#!/bin/bash
cd c:\Users\win\the_first\response-network\api
uvicorn main:app --host 0.0.0.0 --port 8000 > server.log 2>&1
