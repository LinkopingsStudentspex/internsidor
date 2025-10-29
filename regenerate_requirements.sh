# Generates both dev and prod requirement files to ensure consistency
uv export --no-hashes -o requirements-dev.txt
uv export --extra production --no-hashes -o requirements-prod.txt
