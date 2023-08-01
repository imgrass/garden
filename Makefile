# Metadata
PROJECT := imgrass-horizon
MODULE := imgrass_horizon
VERSION := 0.1.0
DESCRIPTION := A beautiful frontend to manage the work machine
README := README.md
AUTHOR := dew.spark
AUTHOR_EMAIL := imgrass201@163.com
URL := https://github.com/imgrass/horizon.git
LICENSE := MIT
PYTHON_REQUIRES := >=3.6


DIR_ROOT := $(shell realpath .)
DIR_CONFIG := $(DIR_ROOT)/config
DIR_SCRIPT := $(DIR_ROOT)/scripts
DIR_SOURCE_CODE := $(DIR_ROOT)/src
DIR_SOURCE_TEST := $(DIR_SOURCE_CODE)/tests
DIR_SOURCE_ROBOT := $(DIR_SOURCE_CODE)/robots
DIR_BUILD := $(DIR_ROOT)/build
DIR_BUILD_INSTALL := $(DIR_BUILD)/sdist
DIR_BUILD_SOURCE := $(DIR_BUILD_INSTALL)/$(MODULE)
DIR_BUILD_TEST := $(DIR_BUILD_SOURCE)/tests
DIR_BUILD_ROBOT := $(DIR_BUILD_SOURCE)/robots


SETUP_PY := $(DIR_BUILD_INSTALL)/setup.py
SETUP_CFG := $(DIR_BUILD_INSTALL)/setup.cfg
SERVICE := $(PROJECT)-api-server.service
BUILD_SERVICE := $(DIR_BUILD_INSTALL)/$(SERVICE)
SYSTEM_SERVICE := /etc/systemd/system/$(SERVICE)

SOURCE_CODES_PY := $(shell find $(DIR_SOURCE_CODE) -type d -name tests -prune \
				   		   						   -type d -name robots -prune -o \
				   		   						   -name "*.py" -type f -printf '%p ')
BUILD_CODES_PY := $(patsubst $(DIR_SOURCE_CODE)/%,$(DIR_BUILD_SOURCE)/%,$(SOURCE_CODES_PY))
BUILD_CODES_DIR := $(sort $(dir $(BUILD_CODES_PY)))

SOURCE_CODES_CFG := requirements.txt test-requirements.txt upper-constraints.txt \
					tox.ini
SOURCE_CODES_CFG := $(patsubst %,$(DIR_CONFIG)/%,$(SOURCE_CODES_CFG))
BUILD_CODES_CFG := $(patsubst $(DIR_CONFIG)/%,$(DIR_BUILD_INSTALL)/%,$(SOURCE_CODES_CFG))

REQUIREMENTS_INSTALL := requirements.txt upper-constraints.txt
REQUIREMENTS_INSTALL := $(patsubst %,$(DIR_BUILD_INSTALL)/%,$(REQUIREMENTS))
REQUIREMENTS_TEST := $(REQUIREMENTS_INSTALL) $(DIR_BUILD_INSTALL)/test-requirements.txt
PIP_INSTALL_REQUIREMENTS := -c $(DIR_BUILD_INSTALL)/upper-constraints.txt \
							-r $(DIR_BUILD_INSTALL)/requirements.txt

SOURCE_CODES_TEST := $(shell find $(DIR_SOURCE_TEST) -type f -name "*.py" -type f -printf '%p ')
BUILD_CODES_TEST := $(patsubst $(DIR_SOURCE_TEST)/%,$(DIR_BUILD_TEST)/%,$(SOURCE_CODES_TEST))
BUILD_CODES_TEST_DIR := $(sort $(dir $(BUILD_CODES_TEST)))

SOURCE_CODES_ROBOT := $(shell find $(DIR_SOURCE_ROBOT) -type f -printf '%p ')
BUILD_CODES_ROBOT := $(patsubst $(DIR_SOURCE_ROBOT)/%,$(DIR_BUILD_ROBOT)/%,$(SOURCE_CODES_ROBOT))
BUILD_CODES_ROBOT_DIR := $(sort $(dir $(BUILD_CODES_ROBOT)))


$(DIR_BUILD) $(DIR_BUILD_INSTALL) $(DIR_BUILD_SOURCE) $(BUILD_CODES_DIR) \
	$(BUILD_CODES_TEST_DIR) $(BUILD_CODES_ROBOT_DIR):
	mkdir -p $@


$(BUILD_CODES_PY): $(DIR_BUILD_SOURCE)/%: $(DIR_SOURCE_CODE)/% | $(BUILD_CODES_DIR)
	cp $< $@


$(BUILD_CODES_CFG): $(DIR_BUILD_INSTALL)/%: $(DIR_CONFIG)/% | $(DIR_BUILD_INSTALL)
	cp $< $@


$(BUILD_CODES_TEST): $(DIR_BUILD_TEST)/%: $(DIR_SOURCE_TEST)/% | $(BUILD_CODES_TEST_DIR)
	cp $< $@


$(BUILD_CODES_ROBOT): $(DIR_BUILD_ROBOT)/%: $(DIR_SOURCE_ROBOT)/% | $(BUILD_CODES_ROBOT_DIR)
	cp $< $@


define common_func
	bash $(1) $(DIR_SCRIPT)/common_functions.sh $(2)
endef


define msg
	@printf '\n%s\n  %s%s\n\n' \
		"====== Do $(1)" \
		"(^_<) $(patsubst $(abspath $(OUTPUT))/%,%,$(2))"	\
		"$(if $(3), $(3))";
endef


.PHONY: clean purge tox doc build_source_codes pip-install pip-uninstall \
	install-service uninstall-service develop undevelop


all:
	@echo TODO ...


build_source_codes: $(DIR_BUILD_SOURCE) $(BUILD_CODES_PY) $(BUILD_CODES_CFG)
	@echo "All source codes are updated to build"
	@echo "Generate $(SETUP_PY)"
	@echo -e "from setuptools import setup" \
			 "\nsetup()" \
	> $(SETUP_PY)
	@echo "Generate $(SETUP_CFG)"
	@echo -e "[metadata]" \
	         "\nname = $(PROJECT)" \
	         "\nversion = $(VERSION)" \
	         "\ndescription = $(DESCRIPTION)" \
	         "\nlong_description = file:$(README)" \
	         "\nauthor = $(AUTHOR)" \
	         "\nauthor_email = $(AUTHOR_EMAIL)" \
	         "\nurl = $(URL)" \
	         "\nlicense = $(LICENSE)" \
	         "\n" \
	         "\n[options]" \
	         "\npython_requires = $(PYTHON_REQUIRES)" \
	> $(SETUP_CFG)


pip-install: $(DIR_BUILD_INSTALL) build_source_codes $(REQUIREMENTS_INSTALL)
	pushd $< && pip install $(PIP_INSTALL_REQUIREMENTS) -e .
	pip show $(PROJECT)


pip-uninstall:
	pip uninstall -y $(PROJECT)


install-service:
	@echo -e "[Unit]" \
			 "\nDescription=Horizon API server" \
			 "\n" \
			 "\n[Install]" \
			 "\nWantedBy=multi-user.target" \
			 "\n" \
			 "\n[Service]" \
			 "\nUser=eouylei" \
			 "\nGroup=wheel" \
			 "\nExecStart=python3 -m $(MODULE).api_server" \
	> $(BUILD_SERVICE)
	sudo cp $(BUILD_SERVICE) $(SYSTEM_SERVICE)
	sudo systemctl daemon-reload
	sudo systemctl enable $(SERVICE)
	sudo systemctl start $(SERVICE)
	systemctl status $(SERVICE)


uninstall-service:
	sudo systemctl disable $(SERVICE) || echo "No need to disable $(SERVICE)"
	sudo systemctl stop $(SERVICE) || echo "No need to stop $(SERVICE)"
	sudo rm -f $(SYSTEM_SERVICE)
	sudo systemctl daemon-reload


develop: pip-install install-service
	@$(call msg,,Develop $(PROJECT),)
	@echo "Develop $(PROJECT) successfully (^_<) ..."


undevelop: uninstall-service pip-uninstall
	@$(call msg,,Undevelop $(PROJECT),)
	@echo "Undevelop $(PROJECT) successfully (^_<) ..."


doc:
	@echo Build documents under doc/*, only html format supported now
	make -C doc html


doc-view: doc
	pushd ./doc/build/html && python3 -m http.server


bpf:
	@echo "========================================"
	@echo "+ BPF tools"
	make -C tasks/bpf_tools $(args) DIR_BUILD=$(DIR_BUILD)/bpf_tools


pxe:
	@echo "========================================"
	@echo "+ PXE ..."
	make -C tasks/pxe $(args) DIR_BUILD=$(DIR_BUILD)/pxe


# pushd build/appImage && ARCH=x86_64 appimage --comp xz .


cee-service:
	@python3 tasks/cee_service.py $(args)


diff-inv:
	@python3 tasks/diff_inv.py $(args)


service:
	@pushd src/lib && python3 service.py $(args)


test:
	python3 src/test_lib/algorithm_follower.py


build_test_source_codes: build_source_codes $(REQUIREMENTS_TEST) \
		$(BUILD_CODES_TEST) $(BUILD_CODES_ROBOT)


tox: build_test_source_codes
	$(call msg,Test by tox,tox $(args))
	pushd $(DIR_BUILD_INSTALL) && export MODULE=$(MODULE); tox $(args) || echo
ifeq ($(word 2,$(args)),robot)
	pushd $(DIR_BUILD_INSTALL) && python -m http.server
endif


tox-clean:
	rm -rf $(DIR_BUILD_TEST) $(DIR_BUILD_INSTALL)/.tox \
		$(DIR_BUILD_INSTALL)/tox.ini


coverage:
	$(call common_func, do_tox -e coverage)
	@echo


clean:
	rm -rf $(DIR_BUILD_INSTALL)


purge: clean
	rm -rf $(DIR_BUILD)
