uv build
TOKEN=$(grep "password.*pypi" ~/.pypirc | cut -d: -f2 | tr -d ' ')
uv publish --token "$TOKEN"
