# Makefile for preparing Lambda deployment packages with shared client code


LAMBDA_DIRS = lambda/volunteers lambda/activitylogs lambda/ics214 lambda/auth
CLIENT_SRC = lambda/client
REQUIREMENTS = requirements.txt



.PHONY: all clean prepare-lambdas install-deps extract-fields



all: install-deps extract-fields prepare-lambdas
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


prepare-lambdas:
	@echo "Copying shared client/ code into each Lambda directory..."
	@for dir in $(LAMBDA_DIRS); do \
		rm -rf $$dir/client; \
		cp -r $(CLIENT_SRC) $$dir/; \
	done
	@echo "Done copying client/."


install-deps:
	@echo "Installing Python dependencies into each Lambda directory..."
	@for dir in $(LAMBDA_DIRS); do \
		if [ -f $(REQUIREMENTS) ]; then \
			pip install --upgrade -r $(REQUIREMENTS) -t $$dir; \
		fi; \
		if [ -f $$dir/requirements.txt ]; then \
			pip install --upgrade -r $$dir/requirements.txt -t $$dir; \
		fi; \
	done
	@echo "Done installing dependencies."



clean:
	@echo "Cleaning all subdirectories and dependencies from Lambda directories..."
	@for dir in $(LAMBDA_DIRS); do \
		find $$dir -mindepth 1 -maxdepth 1 -type d -exec rm -rf {} +; \
		find $$dir -name 'six.py' -delete; \
		find $$dir -name '*.pyc' -delete; \
	done
	@echo "Done."
