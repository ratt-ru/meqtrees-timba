DIRS = AppAgent VisAgent MSVisAgent OctoAgent AppUtils Solver

all:
	$(foreach dir,$(DIRS),(cd $(dir)/build/gnu3_debug && make) &&) echo done

all_opt:
	$(foreach dir,$(DIRS),(cd $(dir)/build/gnu3_opt && make) &&) echo done
  
all_dopt:
	$(foreach dir,$(DIRS),(cd $(dir)/build/gnu3_dopt && make) &&) echo done
  
check:
	$(foreach dir,$(DIRS),(cd $(dir)/build/gnu3_debug && make check)&&) echo done
  
aids:
	$(foreach dir,$(DIRS),(cd $(dir)/build/gnu3_debug && make aids)&&) echo done

.PHONY: config configure

config: configure

configure:
	$(foreach dir,$(DIRS),(cd $(dir) && ./bootstrap && cd build/gnu3_debug && ../../lofarconf)&&) echo done

configure_opt:
	$(foreach dir,$(DIRS),(cd $(dir) && ./bootstrap && cd build/gnu3_opt && ../../lofarconf)&&) echo done

configure_dopt:
	$(foreach dir,$(DIRS),(cd $(dir) && ./bootstrap && cd build/gnu3_dopt && ../../lofarconf)&&) echo done
