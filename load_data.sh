#!/usr/bin/env bash
# Loads the Gift and Bliss Supplies dataset into your own private database.
# The data is part of your enrolment, so it is fetched with your personal token.
set -e
TOKEN="${GBS_TOKEN:-}"
if [ -z "$TOKEN" ]; then
  echo "Paste your personal token from your cvfine.com project page (it starts with gbs_), then press Enter:"
  read -r TOKEN
fi
mkdir -p /tmp/gbs && cd /tmp/gbs && rm -rf kit kit.zip
curl -fsS -H "Authorization: Bearer $TOKEN" https://cvfine.com/api/v1/gbs/kit -o kit.zip || { echo "Could not fetch the data. Check the token and try again."; exit 1; }
unzip -q kit.zip -d kit
D=$(find kit -type d -name data | head -1)
cd - >/dev/null
DB="${DATABASE_URL:-postgresql://postgres:learner@db:5432/gbs}"
psql "$DB" -v ON_ERROR_STOP=1 -q -f schema.sql
for t in customers products orders order_items returns regional_managers region_targets; do
  psql "$DB" -v ON_ERROR_STOP=1 -q -c "\copy $t FROM '/tmp/gbs/$D/$t.csv' CSV HEADER"
done
psql "$DB" -c "SELECT COUNT(*) AS orders FROM orders;"
echo "Done. You should see 5000 orders above."
