#!/bin/bash


URL="https://nswrentalbonds.info/"
PAGES=("data" "about")
PAGE_DATE="2024-04-13"
FILE_PREFIX="_file/data/"
FILES=("holdings*.csv" "refunds-portions*.csv" "refunds-totals*.csv")
CURR_DATE=$(date +"%Y-%m-%d")
CHANGE_FREQ="monthly"

# Create new sitemap
exec 1> sitemap.xml

# Write head
echo '<?xml version="1.0" encoding="UTF-8"?>'
echo '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'

# Write root URL
echo "<url>"
echo " <loc>${URL}${endpoint}</loc>"
echo " <lastmod>${PAGE_DATE}</lastmod>"
echo " <changefreq>${CHANGE_FREQ}</changefreq>"
echo " <priority>1.0</priority>"
echo "</url>"

# Write page URLs
for endpoint in "${PAGES[@]}"; do
  echo "<url>"
  echo " <loc>${URL}${endpoint}</loc>"
  echo " <lastmod>$PAGE_DATE</lastmod>"
  echo " <changefreq>$CHANGE_FREQ</changefreq>"
  echo " <priority>0.8</priority>"
  echo "</url>"
done

# Write file URLs
for file in "${FILES[@]}"; do
  filename=$(ls dist/_file/data/${file})
  echo "<url>"
  echo " <loc>${URL}${FILE_PREFIX}${filename}</loc>"
  echo " <lastmod>${CURR_DATE}</lastmod>"
  echo " <changefreq>${CHANGE_FREQ}</changefreq>"
  echo " <priority>0.5</priority>"
  echo "</url>"
done

# print foot
echo "</urlset>"
