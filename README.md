# MCE-Ryzen-Decoder
## Description

MCE Ryzen Decoder for AMD 17h (23) family.
$ cat /proc/cpuinfo | grep family

Developed by Dimitri Fourny.


## Usage

    ./run.py
    USAGE: ./run.py <bank_number> <status_code>


## Example

If you get this following error in the *journalctl*:

    Jul 20 16:11:50 archlinux kernel: mce: [Hardware Error]: Machine check events logged
    Jul 20 16:11:50 archlinux kernel: mce: [Hardware Error]: CPU 10: Machine Check: 0 Bank 5: bea0000000000108
    Jul 20 16:11:50 archlinux kernel: mce: [Hardware Error]: TSC 0 ADDR 1ffff9610d110 MISC d012000101000000 SYND 4d000000 IPID 500b000000000 
    Jul 20 16:11:50 archlinux kernel: mce: [Hardware Error]: PROCESSOR 2:800f11 TIME 1532095761 SOCKET 0 APIC c microcode 800111c

The only insteresting values are *Bank 5: bea0000000000108*.
You just need to put these values in the parameters:

    $ ./run.sh 5 bea0000000000108
    Bank: Execution Unit (EX)
    Error: Watchdog Timeout error (WDT 0x0)   


## How to fix 
### 0xbea0000000000108

    Bank: Execution Unit (EX)
    Error: Watchdog Timeout error (WDT 0x0)

It's the most known error on a Ryzen.
To fix it, you need to disable *C-States* in the *BIOS* or to set the boot parameter *processor.max_cstate=5*.

Usefull discussion about this error: https://community.amd.com/thread/216084?start=75&tstart=0