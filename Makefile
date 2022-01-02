.PHONY: test create_environment create_kernel cryptInit cryptAddUsers cryptListUsers

#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
PROJECT_NAME = $(shell basename $(CURDIR))
PROJECT_CODE = $(shell echo $(PROJECT_NAME) | cut -c1-3 | tr [a-z] [A-Z])
PYTHON_INTERPRETER = python3

#################################################################################
# COMMANDS                                                                      #
#################################################################################

check_python_version:  # Python 3.8 required
	@hash $(PYTHON_INTERPRETER) 2> /dev/null \
		&& [ `$(PYTHON_INTERPRETER) -V 2>&1 | sed 's/.* \([0-9]\).\([0-9]\).*/\1\2/'` -eq "39" ] \
		&& exit 0 \
		|| (echo "Python 3.9 required" 1>&2; exit 1)


## Set up python interpreter environment
create_environment: check_python_version

	@echo CREATE ENVIRONMENT
	$(PYTHON_INTERPRETER) -m pip install -q virtualenv virtualenvwrapper
	@echo ">>> Installing virtualenvwrapper if not already installed.\nMake sure the following lines are in shell startup file\n\
	export WORKON_HOME=$$HOME/.virtualenvs\nexport PROJECT_HOME=$$HOME/Devel\nsource /usr/local/bin/virtualenvwrapper.sh\n\n\
	If you are on Ubuntu >= 17.04, make sure that ~/.local/bin is in your PATH and instead add:\n\
	export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3\nexport WORKON_HOME=$HOME/.virtualenvs\nexport PROJECT_HOME=$$HOME/Devel\n\
	source ~/.local/bin/virtualenvwrapper.sh"
	@bash -c "source `which virtualenvwrapper.sh`;mkvirtualenv $(PROJECT_NAME) --python=$(PYTHON_INTERPRETER)"
	@echo ">>> New virtualenv created. Activate with:\nworkon $(PROJECT_NAME)"
	@echo "PATH_ROOT=$(CURDIR)" > .env.local
	@echo "PROJECT_CODE=$(PROJECT_CODE)" >> .env.local

## setup kernel
create_kernel:
	$(PYTHON_INTERPRETER) -m pip install -q ipykernel
	$(PYTHON_INTERPRETER) -m ipykernel install --user --name $(PROJECT_NAME)
	@echo "Kernel is set up"


path = $(shell aws s3api list-objects --bucket "axom-public-gpg-keys"  --query "Contents[].{Key: Key}" --output text)

## init git-crypt
cryptInit:
    $(git-crypt init)

## add all gpg users
cryptAddUsers:
	for user in $(path);\
	do\
		echo ===== AJOUT USER $$user =====; \
		git-crypt add-gpg-user $$user;\
    done

.DEFAULT_GOAL := help
.PHONY: help
help:
	@echo "$$(tput bold)Available rules:$$(tput sgr0)"
	@echo
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| LC_ALL='C' sort --ignore-case \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=19 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| more $(shell test $(shell uname) = Darwin && echo '--no-init --raw-control-chars')
