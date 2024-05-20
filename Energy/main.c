#include "utils.h"
#include "msrTools.h"
#include <stdio.h>
#include <stdlib.h>


int main(int argc, char *argv[]) {

    if (strcmp(argv[1], "-checkCPU") == 0){
        printf("Checking CPU...\n");
        checkCPU();
    } else if(strcmp(argv[1], "-before") == 0) {
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
