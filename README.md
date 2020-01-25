## Ipsetop

Ipsetop is an iftop like tool that uses ipsets to mesure bandwidth usage.
Contrary to iftop, this tool does not need to copy all packets to userspace using the libpcap,
it instead uses in-kernel counters contained in ipsets. This allow less flexibility on
what is mached exactly, but improve greatly cpu usage.
