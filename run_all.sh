#!/usr/bin/env bash
# Runs the whole prototype end to end.
set -e
python step1_build_db.py
echo; echo "===== STEP 2: raw SQL attempts ====="; python step2_raw_sql.py
echo; echo "===== STEP 3: semantic layer ====="; python step3_demo.py
echo; echo "===== STEP 4: MCP server + agent client ====="; python step4_agent_client.py 2>/dev/null
echo; echo "===== STEP 5: evaluation + gap matrix ====="; python step5_eval.py
