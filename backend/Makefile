venv_dir=venv
python3=python3

check: $(venv_dir)/packages-installed
	$(venv_dir)/bin/python3 -m pytest -vv --tb=native $(pytest_args) tests

run: $(venv_dir)/packages-installed
	ALLOW_DEV_LOGIN=1 $(venv_dir)/bin/cw-backend

venv: $(venv_dir)/packages-installed

$(venv_dir)/packages-installed: requirements.txt requirements-tests.txt
	$(python3) -c "import sys; print('Your Python: '+'.'.join(map(str, sys.version_info[:3]))) ; assert sys.version_info >= (3,6), 'Sorry Python <3.6 is not supported'"
	test -d $(venv_dir) || $(python3) -m venv $(venv_dir)
	$(venv_dir)/bin/pip install -U pip wheel
	$(venv_dir)/bin/pip install -r requirements.txt
	$(venv_dir)/bin/pip install -r requirements-tests.txt
	$(venv_dir)/bin/pip install -e .
	touch $@
