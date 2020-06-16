SERVICE_NAME := gnupg-tools
APP_NAME := gnupg-tools
APP_COMPONENT := gnupg-tools-cli
VERSION ?= commit_$(shell git rev-parse --short HEAD)

DOCKER_HUB := docker.io/akino1976
ENVIRONMENT := prod
CURRENT_DATE := $(shell echo `date +'%Y-%m-%d'`)
PROFILE := medhelp

export VERSION
export ENVIRONMENT
export APP_NAME
export APP_COMPONENT

buildimages:
	docker build \
		-t $(SERVICE_NAME):latest \
		-t $(SERVICE_NAME):$(VERSION) \
		-t $(DOCKER_HUB)/$(SERVICE_NAME):latest \
		-t $(DOCKER_HUB)/$(SERVICE_NAME):$(VERSION) \
		src

date:
	@echo $(CURRENT_DATE)

version:
	@echo ${VERSION}

profile:
	@echo ${PROFILE}

generate-keys: buildimages
	docker run --rm -it \
		-e ENVIRONMENT=${ENVIRONMENT} \
		-e VERSION=${VERSION} \
		--name src \
		--mount type=bind,source="${PWD}"/GNUPG_KEYS,target="/GNUPG_KEYS" \
		--mount type=bind,source="${PWD}"/GNUPG_ASSETS,target="/GNUPG_ASSETS" \
		gnupg-tools:$(VERSION) \
		generate-keys \
		--company-name company \
		--secret-key /GNUPG_KEYS/company/company_test_secret_keys.asc \
		--target-folder /GNUPG_ASSETS/COMPANY

decrypt-file: buildimages
	docker run --rm -it \
		-e ENVIRONMENT=${ENVIRONMENT} \
		-e VERSION=${VERSION} \
		-e AWS_ACCESS_KEY_ID=$(strip $(shell aws configure get aws_access_key_id --profile $(PROFILE))) \
		-e AWS_SECRET_ACCESS_KEY=$(strip $(shell aws configure get aws_secret_access_key --profile $(PROFILE))) \
		--name src \
		--mount type=bind,source="${PWD}"/GNUPG_KEYS,target="/GNUPG_KEYS" \
		--mount type=bind,source="${PWD}"/GNUPG_ASSETS,target="/GNUPG_ASSETS" \
		gnupg-tools:$(VERSION) \
		decrypt-file \
		--target-folder /GNUPG_ASSETS/COMPANY

encrypt-file: buildimages
	docker run --rm -it \
		-e ENVIRONMENT=${ENVIRONMENT} \
		-e AWS_ACCESS_KEY_ID=$(strip $(shell aws configure get aws_access_key_id --profile $(PROFILE))) \
		-e AWS_SECRET_ACCESS_KEY=$(strip $(shell aws configure get aws_secret_access_key --profile $(PROFILE))) \
		--name src \
		--mount type=bind,source="${PWD}"/GNUPG_KEYS,target="/GNUPG_KEYS" \
		--mount type=bind,source="${PWD}"/GNUPG_ASSETS,target="/GNUPG_ASSETS" \
		gnupg-tools:$(VERSION) \
		encrypt-file \
		--target-folder /GNUPG_ASSETS/COMPANY

save-ssm: buildimages
	docker run --rm -it \
        -e ENVIRONMENT=${ENVIRONMENT} \
		-e AWS_ACCESS_KEY_ID=$(strip $(shell aws configure get aws_access_key_id --profile $(PROFILE))) \
		-e AWS_SECRET_ACCESS_KEY=$(strip $(shell aws configure get aws_secret_access_key --profile $(PROFILE))) \
        --name src \
		--mount type=bind,source="${PWD}"/GNUPG_KEYS,target="/GNUPG_KEYS" \
		--mount type=bind,source="${PWD}"/GNUPG_ASSETS,target="/GNUPG_ASSETS" \
		gnupg-tools:$(VERSION) \
        save_ssm \
        --secret-key /GNUPG_KEYS/COMPANY/ \
        --target-folder /GNUPG_ASSETS/COMPANY

build-%:
	docker-compose -f docker-compose.yml build $*

stop-all-containers:
	docker ps -q | xargs -I@ docker stop @

clear-all-containers: stop-all-containers
	docker ps -aq | xargs -I@ docker rm @

clear-volumes: clear-all-containers
	docker volume ls -q | xargs -I@ docker volume rm @

clear-images: clear-volumes
	docker images -q | uniq | xargs -I@ docker rmi -f @

clear-build-files:
	find . | grep "build[^/]*commit_[0-9a-f]\{7\}$$" | xargs rm -rf

clear-pytest-cache:
	sudo find . | grep -E "(\.pytest_cache)" | xargs rm -rf

clear-pycache:
	sudo find . | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf

run-%:
	docker-compose $(COMPOSE_DEFAULT_FLAGS) run --rm $*

build-%:
	docker-compose $(COMPOSE_DEFAULT_FLAGS) build $*
