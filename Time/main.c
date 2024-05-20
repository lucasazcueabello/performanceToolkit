#include "utils.h"
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int measure_clock(int isBefore, int line){
	struct timespec timestamp;
	clock_gettime(CLOCK_MONOTONIC, &timestamp);
	double time = (timestamp.tv_sec + (timestamp.tv_nsec / 1000000000.0));
	isBefore == 0 ? writeFile("clock_output.txt", time) : appendToFile("clock_output.txt", time, line);
	return 0;
}

void makeMeasurment(int isBefore, int line){
	int result = -1;

	result = measure_clock(isBefore, line);

	if (result<0) {
		printf("Unable to read clock values.\n");
		printf("\n");
	}

}

int main(int argc, char *argv[]) {

    if(strcmp(argv[1], "-before") == 0) {
        makeMeasurment(0, -1);
    } else if (strcmp(argv[1], "-after") == 0) {
        makeMeasurment(1, -1);
    } else if (atoi(argv[1]) > -1) {
        makeMeasurment(1, atoi(argv[1]));
    } else {
        printf("Invalid argument: %s\n", argv[1]);
        return 1;
    }

    return 0;
}
