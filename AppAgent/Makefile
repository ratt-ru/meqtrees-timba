DIRS = AppAgent VisAgent MSVisAgent OctoAgent AppUtils Solver

all:
	$(foreach dir,$(DIRS),(cd $(dir)/build/gnu3_debug && make) &&) echo done
  
check:
	$(foreach dir,$(DIRS),(cd $(dir)/build/gnu3_debug && make check)&&) echo done
  
aids:
	$(foreach dir,$(DIRS),(cd $(dir)/build/gnu3_debug && make aids)&&) echo done
