CC=gcc
CFLAGS=-Wall -g -O2
LDFLAGS=-lm

SRCS=main.c utils.c msrTools.c
OBJS=$(SRCS:.c=.o)
EXEC=energyTool

all: $(EXEC)

$(EXEC): $(OBJS)
	$(CC) $(OBJS) -o $@ $(LDFLAGS)

main.o: main.c utils.h msrTools.h
	$(CC) $(CFLAGS) -c $< -o $@

utils.o: utils.c utils.h
	$(CC) $(CFLAGS) -c $< -o $@

msrTools.o: msrTools.c msrTools.h
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(EXEC) $(OBJS)
