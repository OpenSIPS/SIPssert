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

Alternatively, configure sudo to bypass the `PYTHONPATH` variable: add in the
`/etc/sudoers.d/python` (or direcly in `/etc/sudoers`) the following line:
```
Defaults env_keep += "PYTHONPATH"
```
