SUBDIRS = eispack plotlib bin

all: $(SUBDIRS)

.PHONY: $(SUBDIRS)

$(SUBDIRS):
	$(MAKE) -C $@ $(MFLAGS)

clean:
	-for d in $(SUBDIRS); do ( $(MAKE) -C $$d clean ); done

