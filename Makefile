# Makefile for preparing Lambda deployment packages with shared client code
# and installing shared Python dependencies.

LAYER_BUILD_DIR = shared/python




.PHONY: all clean install-deps extract-fields dev-venv



all: install-deps extract-fields
extract-fields:
	@echo "Extracting fields JSON from PDF templates in lambda/reports..."
	cd lambda/reports && \
	for pdf in *.pdf; do \
		json="$${pdf%.pdf}.json"; \
		if [ ! -f "$${json}" ]; then \
			python extract_fields.py "$${pdf}" "$${json}"; \
		fi; \
	done
	@echo "Done extracting fields JSON."




install-deps: clean
	@echo "Installing EventCoord package and dependencies for Lambda Layer..."
	mkdir -p $(LAYER_BUILD_DIR)
	pip install . -t $(LAYER_BUILD_DIR)
	@echo "Done installing EventCoord and dependencies."




dev-venv:
	@echo "Setting up local development virtual environment..."
	python3 -m venv venv
	. venv/bin/activate && \
		pip install --upgrade pip && \
		pip install -e .
	@echo "Local dev venv ready. Run: source venv/bin/activate"



clean:
	@echo "Cleaning all shared dependencies for Lambda Layer..."
	@rm -rf $(dir $(LAYER_BUILD_DIR))
	@echo "Done."
