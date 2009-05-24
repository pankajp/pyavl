
#FC = f77
FC = f95
FLG = -O
EISLIB = eispack.a
AR = ar r
RAN = ranlib



eispack.a: eispack.o
	$(FC) -c $(FLG) eispack.f
	$(AR) $(EISLIB) eispack.o
	$(RAN) $(EISLIB)

clean:
	/bin/rm *.o *.a


