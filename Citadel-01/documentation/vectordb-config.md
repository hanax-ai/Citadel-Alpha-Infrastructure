agent0@hx-vector-database-server:~$ lscpu
free -h
lsblk -o NAME,SIZE,FSTYPE,MOUNTPOINT
df -hT --total
Architecture:             x86_64
  CPU op-mode(s):         32-bit, 64-bit
  Address sizes:          39 bits physical, 48 bits virtual
  Byte Order:             Little Endian
CPU(s):                   16
  On-line CPU(s) list:    0-15
Vendor ID:                GenuineIntel
  Model name:             Intel(R) Core(TM) i9-9900K CPU @ 3.60GHz
    CPU family:           6
    Model:                158
    Thread(s) per core:   2
    Core(s) per socket:   8
    Socket(s):            1
    Stepping:             13
    CPU(s) scaling MHz:   19%
    CPU max MHz:          5000.0000
    CPU min MHz:          800.0000
    BogoMIPS:             7200.00
    Flags:                fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp l                          m constant_tsc art arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc cpuid aperfmperf pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 s                          sse3 sdbg fma cx16 xtpr pdcm pcid sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm 3dnowprefetch cpuid_fa                          ult epb ssbd ibrs ibpb stibp ibrs_enhanced tpr_shadow flexpriority ept vpid ept_ad fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid mpx rdseed 
                          adx smap clflushopt intel_pt xsaveopt xsavec xgetbv1 xsaves dtherm ida arat pln pts hwp hwp_notify hwp_act_window hwp_epp vnmi md_clear flush_l1d a                          rch_capabilities
Virtualization features:  
  Virtualization:         VT-x
Caches (sum of all):      
  L1d:                    256 KiB (8 instances)
  L1i:                    256 KiB (8 instances)
  L2:                     2 MiB (8 instances)
  L3:                     16 MiB (1 instance)
NUMA:                     
  NUMA node(s):           1
  NUMA node0 CPU(s):      0-15
Vulnerabilities:          
  Gather data sampling:   Mitigation; Microcode
  Itlb multihit:          KVM: Mitigation: VMX disabled
  L1tf:                   Not affected
  Mds:                    Not affected
  Meltdown:               Not affected
  Mmio stale data:        Mitigation; Clear CPU buffers; SMT vulnerable
  Reg file data sampling: Not affected
  Retbleed:               Mitigation; Enhanced IBRS
  Spec rstack overflow:   Not affected
  Spec store bypass:      Mitigation; Speculative Store Bypass disabled via prctl
  Spectre v1:             Mitigation; usercopy/swapgs barriers and __user pointer sanitization
  Spectre v2:             Mitigation; Enhanced / Automatic IBRS; IBPB conditional; RSB filling; PBRSB-eIBRS SW sequence; BHI SW loop, KVM SW loop
  Srbds:                  Mitigation; Microcode
  Tsx async abort:        Mitigation; TSX disabled
               total        used        free      shared  buff/cache   available
Mem:            78Gi       1.1Gi        76Gi       1.7Mi       1.1Gi        77Gi
Swap:          8.0Gi          0B       8.0Gi
NAME         SIZE FSTYPE MOUNTPOIN
sda          3.6T        
sdb          7.3T        
sdc          7.3T        
nvme0n1      3.6T        
├─nvme0n1p1    1G vfat   /boot/efi
└─nvme0n1p2  3.6T ext4   /
Filesystem     Type      Size  Used Avail Use% Mounted on
tmpfs          tmpfs     7.9G  1.5M  7.9G   1% /run
efivarfs       efivarfs  256K   88K  164K  35% /sys/firmware/efi/efivars
/dev/nvme0n1p2 ext4      3.6T   12G  3.4T   1% /
tmpfs          tmpfs      40G     0   40G   0% /dev/shm
tmpfs          tmpfs     5.0M     0  5.0M   0% /run/lock
/dev/nvme0n1p1 vfat      1.1G  6.2M  1.1G   1% /boot/efi
tmpfs          tmpfs     7.9G   12K  7.9G   1% /run/user/1000
total          -         3.7T   12G  3.5T   1% -
agent0@hx-vector-database-server:~$ 

agent0@hx-vector-database-server:~$ cat /etc/os-release
uname -a
dpkg --list | grep -E 'linux-image|linux-headers'
PRETTY_NAME="Ubuntu 24.04.2 LTS"
NAME="Ubuntu"
VERSION_ID="24.04"
VERSION="24.04.2 LTS (Noble Numbat)"
VERSION_CODENAME=noble
ID=ubuntu
ID_LIKE=debian
HOME_URL="https://www.ubuntu.com/"
SUPPORT_URL="https://help.ubuntu.com/"
BUG_REPORT_URL="https://bugs.launchpad.net/ubuntu/"
PRIVACY_POLICY_URL="https://www.ubuntu.com/legal/terms-and-policies/privacy-policy"
UBUNTU_CODENAME=noble
LOGO=ubuntu-logo
Linux hx-vector-database-server 6.11.0-29-generic #29~24.04.1-Ubuntu SMP PREEMPT_DYNAMIC Thu Jun 26 14:16:59 UTC 2 x86_64 x86_64 x86_64 GNU/Linux
ii  linux-headers-6.11.0-29-generic       6.11.0-29.29~24.04.1                    amd64        Linux kernel headers for version 6.11.0 on 64 bit x86 SMP
ii  linux-headers-generic-hwe-24.04       6.11.0-29.29~24.04.1                    amd64        Generic Linux kernel headers
ii  linux-image-6.11.0-29-generic         6.11.0-29.29~24.04.1                    amd64        Signed kernel image generic
ii  linux-image-generic-hwe-24.04         6.11.0-29.29~24.04.1                    amd64        Generic Linux kernel image
agent0@hx-vector-database-server:~$ dmidecode -t bios | grep -Ei 'Vendor|Version|Release'
ls /sys/firmware/efi && echo "EFI boot mode detected" || echo "Legacy BIOS mode"
/sys/firmware/dmi/tables/smbios_entry_point: Permission denied
Can't read memory from /dev/mem
config_table  efivars  esrt  fw_platform_size  fw_vendor  mok-variables  runtime  runtime-map  systab
EFI boot mode detected
agent0@hx-vector-database-server:~$ lspci | grep -Ei 'vga|3d|nvidia'
nvidia-smi 2>/dev/null || echo "No NVIDIA GPU or driver not installed"
01:00.0 VGA compatible controller: NVIDIA Corporation GP108 [GeForce GT 1030] (rev a1)
01:00.1 Audio device: NVIDIA Corporation GP108 High Definition Audio Controller (rev a1)
No NVIDIA GPU or driver not installed
agent0@hx-vector-database-server:~$ ip a
ip r
hostname -I
ss -tulpn
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host noprefixroute 
       valid_lft forever preferred_lft forever
2: eno1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether a4:bb:6d:56:70:2e brd ff:ff:ff:ff:ff:ff
    altname enp0s31f6
    inet 192.168.10.30/24 brd 192.168.10.255 scope global eno1
       valid_lft forever preferred_lft forever
    inet6 fe80::a6bb:6dff:fe56:702e/64 scope link 
       valid_lft forever preferred_lft forever
default via 192.168.10.1 dev eno1 proto static 
192.168.10.0/24 dev eno1 proto kernel scope link src 192.168.10.30 
192.168.10.30 
Netid            State             Recv-Q            Send-Q                       Local Address:Port                         Peer Address:Port            Process            
udp              UNCONN            0                 0                               127.0.0.54:53                                0.0.0.0:*                                  
udp              UNCONN            0                 0                            127.0.0.53%lo:53                                0.0.0.0:*                                  
tcp              LISTEN            0                 4096                         127.0.0.53%lo:53                                0.0.0.0:*                                  
tcp              LISTEN            0                 4096                            127.0.0.54:53                                0.0.0.0:*                                  
tcp              LISTEN            0                 4096                                     *:22                                      *:*                                  
agent0@hx-vector-database-server:~$ egrep -c '(vmx|svm)' /proc/cpuinfo
systemd-detect-virt
32
none
agent0@hx-vector-database-server:~$ which python3
python3 --version
pip3 list
ls /opt | grep env
/usr/bin/python3
Python 3.12.3
Command 'pip3' not found, but can be installed with:
sudo apt install python3-pip
agent0@hx-vector-database-server:~$ 