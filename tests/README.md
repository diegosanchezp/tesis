Instructions for running the tests that are located in this folder

```bash
load_env envs/production/host
```

To run `tests/resetdb.py`

```bash
docker run --rm \
  -it \
  --workdir /app \
  --mount "type=bind,source=./shscripts/,target=/app/shscripts/" \
  --mount "type=bind,source=./tests/,target=/app/tests/" \
  --env-file envs/production/django \
  --env-file envs/production/postgres \
  --network production_default \
  "$DOCKER_IMAGE" \
  python -m unittest tests.resetdb.TestReset.test_backup_dev
```
