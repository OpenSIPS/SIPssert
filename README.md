## Usage

Run using docker priviledged user:
```
export PYTHONATH=.
bin/testing-framework tests
```

If running using `sudo`, you need to preserve the `PYTHONPATH` variable:
```
sudo -E env PYTHONPATH=. bin/testing-framework tests
```
