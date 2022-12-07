import os

# Check the CPU vendor ID
with open('/proc/cpuinfo') as f:
    for line in f:
        if line.startswith('vendor_id'):
            vendor_id = line.split(':')[1].strip()
            break

# Check if the CPU vendor ID indicates a virtual machine
if vendor_id in ('GenuineIntel', 'AuthenticAMD'):
    # If the CPU vendor ID is GenuineIntel or AuthenticAMD,
    # the script is likely running on a physical machine
    is_vm = False
else:
    # If the CPU vendor ID is not GenuineIntel or AuthenticAMD,
    # the script is likely running on a virtual machine
    is_vm = True

# Check the DMI system vendor string
with open('/sys/class/dmi/id/sys_vendor') as f:
    dmi_vendor = f.read().strip()

# Check if the DMI system vendor string indicates a virtual machine
if dmi_vendor in ('Bochs', 'QEMU', 'VirtualBox', 'VMware'):
    # If the DMI system vendor string is Bochs, QEMU, VirtualBox, or VMware,
    # the script is likely running on a virtual machine
    is_vm = True

# Print the result
if is_vm:
    print('The script is running in a virtual machine')
else:
    print('The script is not running in a virtual machine')