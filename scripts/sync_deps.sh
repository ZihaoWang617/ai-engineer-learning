#!/bin/bash
# scripts/sync_deps.sh
# 用法：./scripts/sync_deps.sh
# diff 当前 venv 和 requirements.txt，需手动确认才覆盖

pip freeze --exclude-editable > requirements.txt.new

if diff -q requirements.txt requirements.txt.new > /dev/null; then
    echo "✅ requirements.txt is in sync."
    rm requirements.txt.new
    exit 0
fi

echo "⚠️  Dependencies drift detected:"
diff requirements.txt requirements.txt.new
echo ""
read -p "Update requirements.txt? [y/N] " ans
if [[ "$ans" == "y" ]]; then
    mv requirements.txt.new requirements.txt
    echo "✅ Updated. Don't forget to commit."
else
    rm requirements.txt.new
    echo "❌ Aborted. No changes made."
fi
