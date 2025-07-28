# Makefile for preparing Lambda deployment packages with shared client code
# and installing shared Python dependencies.

LAYER_BUILD_DIR = shared/build/python
SHARED_REQUIREMENTS = shared/requirements.txt




.PHONY: all clean install-deps extract-fields dev-venv



all: install-deps extract-fields
extract-fields:
	@echo "Extracting fields JSON from PDF templates in lambda/reports..."
	cd lambda/reports && \
	for pdf in *.pdf; do \
		json="$${pdf%.pdf}.json"; \
		if [ ! -f "$${json}" ]; then \
			PYTHONPATH=.${PYTHONPATH:+:$$PYTHONPATH} python extract_fields.py "$${pdf}" "$${json}"; \
		fi; \
	done
	@echo "Done extracting fields JSON."



install-deps: clean
	@echo "Installing shared Python dependencies for Lambda Layer..."
	mkdir -p $(LAYER_BUILD_DIR)
	pip install --upgrade -r $(SHARED_REQUIREMENTS) -t $(LAYER_BUILD_DIR)
	@for dir in shared/*; do \
		if [ -d $$dir ] && [ "$$(basename $$dir)" != "python" ]; then \
			cp -r $$dir $(LAYER_BUILD_DIR)/; \
		fi; \
	done
	@echo "Done installing shared dependencies and copying shared code."



dev-venv:
	@echo "Setting up local development virtual environment..."
	python3 -m venv venv
	. venv/bin/activate && \
		pip install --upgrade pip && \
		pip install -r $(SHARED_REQUIREMENTS)
	@for dir in shared/*; do \
		if [ -d $$dir ] && [ "$$dir" != "shared/build" ]; then \
			. venv/bin/activate && pip install -e $$dir; \
		fi; \
	done
	@echo "Local dev venv ready. Run: source venv/bin/activate"



clean:
	@echo "Cleaning all shared dependencies for Lambda Layer..."
	@rm -rf $(dir $(LAYER_BUILD_DIR))
	@echo "Done."
