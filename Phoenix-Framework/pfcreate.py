import os
curr_dir = os.getcwd()
#os.chdir("/usr/share/phoenix-framework")
import Creator
from globals import *
ph_print(logo)
parser = ArgumentParser("pfcreate", description="Create Payloads to interact with the Phoenix-Framework")
parser.add_argument("-p", "--payload", help="The payload to use", choices=Creator.payloads)
parser.add_argument("-f", "--format", help="The Format to use", choices=Creator.formats, default=".py")
parser.add_argument("-ha", "--haddress", help="The Address of the running the Handler")
parser.add_argument("-hp", "--hport", help="The Port where the Handler is running")
parser.add_argument("-e", "--encoding", help="The Encoding to use", choices=Creator.encoders, default="base64")
parser.add_argument("-o", "--output", help="The output file", default="payload")
parser.add_argument("-l", "--list", help="List the Options of an Argument", choices=["payloads"])
parser.add_argument("-v", "--verbose", help="Verbose Output", action="store_true")
args = parser.parse_args()
if args.list:
    if args.list == "payloads":
        ph_print("Payloads:")
        for format in Creator.payloads:
            ph_print(format)
    exit(0)
if not args.payload:
    ph_print("[!] Please specify a Payload")
    exit(1)
if not args.haddress:
    ph_print("[!] Please specify an address")
    exit(1)
if not args.hport:
    ph_print("[!] Please specify a port")
    exit(1)
if args.verbose:
    verbose = True
else:
    verbose = False
ph_print("[*] Creating Payload")
ph_print("[*] Address: " + args.haddress)
ph_print("[*] Port: " + args.hport)
ph_print("[*] Output: " + args.output + args.format)
# Create the Payload
try:
    payload = Creator.create(args.payload, args.haddress, args.hport, args.encoding)
except Exception as e:
    log(str(e), "error")
    exit(1)
#os.chdir(curr_dir)
with open(args.output + args.format, "w") as f:
    f.write(payload)
if payload:
    ph_print("[*] Payload created successfully")
    exit(0)
else:
    ph_print("[!] Could not create the payload")
    exit(1)
