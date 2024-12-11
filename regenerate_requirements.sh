# Generates both dev and prod requirement files to ensure consistency
pip-compile --output-file=requirements-dev.txt --strip-extras requirements-base.in
pip-compile --output-file=requirements-prod.txt --strip-extras requirements-base.in requirements-prod.in