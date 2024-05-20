#include "utils.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_LINE_LENGTH 1000

#include <stdio.h>

void writeFile(const char *filename, double value, int is_Jules) {
    FILE *file = fopen(filename, "w");
    if (file == NULL) {
        printf("Error opening file!\n");
        return;
    }
    fprintf(file, "%.6f%s\n", value, is_Jules ? "J" : "T");
    fclose(file);
}

void appendToFile(const char *filename, double value, int line, int is_Jules) {
    FILE *file = fopen(filename, "a");
    if (file == NULL) {
        printf("Error opening file!\n");
        return;
    }
    fprintf(file, "%.6f%s", value, is_Jules ? "J" : "T");
    if (line > -1) {
        fprintf(file, " %d", line);
    }
    fprintf(file, "\n");
    fclose(file);
}

