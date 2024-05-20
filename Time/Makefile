CC=gcc
CFLAGS=-Wall -g -O2
LDFLAGS=-lm

SRCS=main.c utils.c
OBJS=$(SRCS:.c=.o)
EXEC=timeTool

all: $(EXEC)

$(EXEC): $(OBJS)
	$(CC) $(OBJS) -o $@ $(LDFLAGS)

main.o: main.c utils.h
	$(CC) $(CFLAGS) -c $< -o $@

utils.o: utils.c utils.h
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(EXEC) $(OBJS)
