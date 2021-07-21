VENV := venv

$(VENV)/bin/activate: requirements.txt
	python3 -m venv $(VENV)
	./$(VENV)/bin/pip install -r requirements.txt

venv: $(VENV)/bin/activate

test:
	pytest -v 

image:
	podman build -t ccm_smoke_test -f Dockerfile 
run:
	podman run --rm ccm_smoke_test

clean:
	rm -rf $(VENV)
	rm -rf .pytest_cache
	rm -rf __pycache__

.PHONY: venv test clean image run


