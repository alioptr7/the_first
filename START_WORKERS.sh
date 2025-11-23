#!/bin/bash
# راهنما برای شروع workers برای هر دو شبکه

# مقدار دهی متغیرهای محیطی
export PYTHONPATH="/workspaces/the_first/request-network/api:/workspaces/the_first"

echo "==================================="
echo "REQUEST NETWORK - BEAT (Terminal 1)"
echo "==================================="
echo ""
echo "کپی کن و در Terminal 1 اجرا کن:"
echo ""
echo 'cd /workspaces/the_first/request-network/api && PYTHONPATH=/workspaces/the_first/request-network/api:/workspaces/the_first celery -A workers.celery_app beat --loglevel=info'
echo ""
echo ""

echo "==================================="
echo "REQUEST NETWORK - WORKER (Terminal 2)"
echo "==================================="
echo ""
echo "کپی کن و در Terminal 2 اجرا کن:"
echo ""
echo 'cd /workspaces/the_first/request-network/api && PYTHONPATH=/workspaces/the_first/request-network/api:/workspaces/the_first celery -A workers.celery_app worker --loglevel=info --concurrency=2'
echo ""
echo ""

echo "==================================="
echo "RESPONSE NETWORK - BEAT (Terminal 3)"
echo "==================================="
echo ""
echo "کپی کن و در Terminal 3 اجرا کن:"
echo ""
echo 'cd /workspaces/the_first/response-network/api && PYTHONPATH=/workspaces/the_first/response-network/api:/workspaces/the_first celery -A workers.celery_app beat --loglevel=info'
echo ""
echo ""

echo "==================================="
echo "RESPONSE NETWORK - WORKER (Terminal 4)"
echo "==================================="
echo ""
echo "کپی کن و در Terminal 4 اجرا کن:"
echo ""
echo 'cd /workspaces/the_first/response-network/api && PYTHONPATH=/workspaces/the_first/response-network/api:/workspaces/the_first celery -A workers.celery_app worker --loglevel=info --concurrency=4'
echo ""

echo "==================================="
echo "Shared Export/Import Directory"
echo "==================================="
echo "📁 Exports: /workspaces/the_first/exports"
echo "📁 Imports: /workspaces/the_first/imports"
