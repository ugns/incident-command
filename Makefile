# Makefile for preparing Lambda deployment packages with shared client code


LAMBDA_DIRS = lambda/volunteers lambda/activitylogs lambda/ics214
CLIENT_SRC = lambda/client
REQUIREMENTS = requirements.txt


.PHONY: all clean prepare-lambdas install-deps


all: install-deps prepare-lambdas


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
