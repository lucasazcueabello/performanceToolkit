#include "msrTools.h"
#include "utils.h"
#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <fcntl.h>
#include <errno.h>
#include <inttypes.h>
#include <unistd.h>
#include <math.h>
#include <string.h>
#include <stdbool.h>
#include <sys/time.h>
#include <time.h>

#include <sys/syscall.h>
#include <linux/perf_event.h>


#define MSR_RAPL_POWER_UNIT		0x606

/*
 * Platform specific RAPL Domains.
 * Note that PP1 RAPL Domain is supported on 062A only
 * And DRAM RAPL Domain is supported on 062D only
 */
/* Package RAPL Domain */
#define MSR_PKG_RAPL_POWER_LIMIT	0x610
#define MSR_PKG_ENERGY_STATUS		0x611
#define MSR_PKG_PERF_STATUS		0x613
#define MSR_PKG_POWER_INFO		0x614

/* PP0 RAPL Domain */
#define MSR_PP0_POWER_LIMIT		0x638
#define MSR_PP0_ENERGY_STATUS		0x639
#define MSR_PP0_POLICY			0x63A
#define MSR_PP0_PERF_STATUS		0x63B

/* PP1 RAPL Domain, may reflect to uncore devices */
#define MSR_PP1_POWER_LIMIT		0x640
#define MSR_PP1_ENERGY_STATUS		0x641
#define MSR_PP1_POLICY			0x642

/* DRAM RAPL Domain */
#define MSR_DRAM_POWER_LIMIT		0x618
#define MSR_DRAM_ENERGY_STATUS		0x619
#define MSR_DRAM_PERF_STATUS		0x61B
#define MSR_DRAM_POWER_INFO		0x61C

/* RAPL UNIT BITMASK */
#define POWER_UNIT_OFFSET	0
#define POWER_UNIT_MASK		0x0F

#define ENERGY_UNIT_OFFSET	0x08
#define ENERGY_UNIT_MASK	0x1F00

#define TIME_UNIT_OFFSET	0x10
#define TIME_UNIT_MASK		0xF000

static int open_msr(int core) {

	char msr_filename[BUFSIZ];
	int fd;

	sprintf(msr_filename, "/dev/cpu/%d/msr", core);
	fd = open(msr_filename, O_RDONLY);
	if ( fd < 0 ) {
		if ( errno == ENXIO ) {
			fprintf(stderr, "rdmsr: No CPU %d\n", core);
			exit(2);
		} else if ( errno == EIO ) {
			fprintf(stderr, "rdmsr: CPU %d doesn't support MSRs\n", core);
			exit(3);
		} else {
			perror("rdmsr:open");
			fprintf(stderr,"Trying to open %s\n",msr_filename);
			exit(127);
		}
	}

	return fd;
}

static long long read_msr(int fd, int which) {

	uint64_t data;

	if ( pread(fd, &data, sizeof data, which) != sizeof data ) {
		perror("rdmsr:pread");
		exit(127);
	}

	return (long long)data;
}

#define CPU_SANDYBRIDGE		42
#define CPU_SANDYBRIDGE_EP	45
#define CPU_IVYBRIDGE		58
#define CPU_IVYBRIDGE_EP	62
#define CPU_HASWELL		60

static int detect_cpu(int isPrintCPU) {

	FILE *fff;

	int family,model=-1;
	char buffer[BUFSIZ],*result;
	char vendor[BUFSIZ];

	fff=fopen("/proc/cpuinfo","r");
	if (fff==NULL) return -1;

	while(1) {
		result=fgets(buffer,BUFSIZ,fff);
		if (result==NULL) break;

		if (!strncmp(result,"vendor_id",8)) {
			sscanf(result,"%*s%*s%s",vendor);

			if (strncmp(vendor,"GenuineIntel",12)) {
				printf("%s not an Intel chip\n",vendor);
				return -1;
			}
		}

		if (!strncmp(result,"cpu family",10)) {
			sscanf(result,"%*s%*s%*s%d",&family);
			if (family!=6) {
				printf("Wrong CPU family %d\n",family);
				return -1;
			}
		}

		if (!strncmp(result,"model",5)) {
			sscanf(result,"%*s%*s%d",&model);
		}

	}

	fclose(fff);

	if(isPrintCPU != 0) {
		switch(model) {
			case CPU_SANDYBRIDGE:
				printf("Found Sandybridge CPU\n");
				break;
			case CPU_SANDYBRIDGE_EP:
				printf("Found Sandybridge-EP CPU\n");
				break;
			case CPU_IVYBRIDGE:
				printf("Found Ivybridge CPU\n");
				break;
			case CPU_IVYBRIDGE_EP:
				printf("Found Ivybridge-EP CPU\n");
				break;
			case CPU_HASWELL:
				printf("Found Haswell CPU\n");
				break;
			default:	
				printf("Unsupported model %d\n",model);
				model=-1;
				break;
		}
	}

	return model;
}


/*******************************/
/* MSR code                    */
/*******************************/
 static int rapl_msr(int core, int time_measure, int isBefore, int line)  {

 	int fd;
 	long long result;
 	double energy_units;
 	double package_energy;
 	int cpu_model;

 	cpu_model=detect_cpu(0);
 	if (cpu_model<0) {
 		printf("Unsupported CPU type\n");
 		return -1;
 	}

 	fd=open_msr(core);

  /* Calculate the units used */
 	result=read_msr(fd,MSR_RAPL_POWER_UNIT);

 	energy_units=pow(0.5,(double)((result>>8)&0x1f));

 	result=read_msr(fd,MSR_PKG_ENERGY_STATUS);
 	package_energy=(double)result*energy_units;
    isBefore == 0 ? writeFile("output.txt", package_energy, 1) : appendToFile("output.txt", package_energy, line, 1);

	close(fd);

	return 0;
}

void makeMeasurment(int isBefore, int line){
    int core = 0;
	int time_measure = 0;
	int result = -1;

	
	result=rapl_msr(core, time_measure, isBefore, line);


	if (result<0) {
		printf("Unable to read RAPL counters.\n");
		printf("* Verify you have an Intel Sandybridge, Ivybridge or Haswell processor\n");
		printf("* You may need to run as root or have /proc/sys/kernel/perf_event_paranoid set properly\n");
		printf("* If using raw msr access, make sure msr module is installed\n");
		printf("\n");
	}

}

void checkCPU(){
	int cpu_model;

 	cpu_model=detect_cpu(1);
 	if (cpu_model<0) {
 		printf("Unsupported CPU type\n");
 		return -1;
 	}
}

