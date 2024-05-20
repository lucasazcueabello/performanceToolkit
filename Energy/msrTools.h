#ifndef MSR_TOOLS_H
#define MSR_TOOLS_H

/* Read the RAPL registers on a sandybridge-ep machine                */
/* Code based on Intel RAPL driver by Zhang Rui <rui.zhang@intel.com> */
/*                                                                    */
/* The /dev/cpu/??/msr driver must be enabled and permissions set     */
/* to allow read access for this to work.                             */
/*                                                                    */
/* Code to properly get this info from Linux through a real device    */
/*   driver and the perf tool should be available as of Linux 3.14    */
/* Compile with:   gcc -O2 -Wall -o rapl-read rapl-read.c -lm         */
/*                                                                    */
/* Vince Weaver -- vincent.weaver @ maine.edu -- 29 November 2013     */
/*                                                                    */
/* Additional contributions by:                                       */
/*   Romain Dolbeau -- romain @ dolbeau.org                           */
/*   David Branco   -- davidbranco88 @ gmail.com --16 May 2015  */

static int open_msr(int core);
static long long read_msr(int fd, int which);
static int detect_cpu(int isPrintCPU);
static int rapl_msr(int core, int time_measure, int isBefore, int line);
int measure_clock(int isBefore, int line);
void makeMeasurment(int isBefore, int line);
void checkCPU();

#endif /* MSR_TOOLS_H */