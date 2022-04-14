from Utils.ui import *
import Creator
import os
import clipboard
curr_dir = os.getcwd()
# os.chdir("/usr/share/phoenix-framework")
ph_print(logo)
parser = ArgumentParser(
    "pfcreate", description="Create Stagers to interact with the Phoenix-Framework")
parser.add_argument("-l", "--listener", help="The Listener to use")
parser.add_argument("-p", "--payload", help="The payload to use")
parser.add_argument("-f", "--format", help="The Format to use", default=".py")
parser.add_argument("-ha", "--haddress",
                    help="The Address of the running the Handler")
parser.add_argument(
    "-hp", "--hport", help="The Port where the Handler is running")
parser.add_argument("-e", "--encoding",
                    help="The Encoding to use", default="base64")
parser.add_argument(
    "-o", "--output", help="The output file", default="payload")
parser.add_argument(
    "-c", "--copy", help="Copy the payload to the clipboard", action="store_true")
parser.add_argument("-s", "--show", help="Show the Options of an Argument")
parser.add_argument("-v", "--verbose",
                    help="Verbose Output", action="store_true")
args = parser.parse_args()
if args.show:
    if args.show == "payloads":
        ph_print("Payloads:")
        for format in Creator.payloads:
            ph_print(format)
    elif args.show == "encoders":
        ph_print("Encoders:")
        for format in Creator.encoders:
            ph_print(format)
    elif args.show == "formats":
        ph_print("Formats:")
        for format in Creator.formats:
            ph_print(format)
    else:
        ph_print("Unknown List")
    exit(0)
if not args.listener:
    ph_print("No Listener specified")
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
if args.payload not in Creator.payloads:
    ph_print(f"[!] Unknown Payload: {args.payload}", alert="error")
    exit(1)
if args.encoding not in Creator.encoders:
    ph_print(f"[!] Unknown Encoding: {args.encoding}", alert="error")
    exit(1)
if args.format not in Creator.formats:
    ph_print(f"[!] Unknown Format: {args.format}", alert="error")
    exit(1)
ph_print("[*] Creating Stager")
ph_print("[*] Address: " + args.haddress)
ph_print("[*] Port: " + args.hport)
output = args.output + args.format if not args.copy else "Clipboard"
ph_print("[*] Output: " + output)
# Create the Payload
try:
    stager = Creator.create(args.listener, args.payload,
                            args.haddress, args.hport, args.encoding)
except Exception as e:
    log(str(e), "error")
    exit(1)
# os.chdir(curr_dir)
if args.copy:
    clipboard.copy(stager)
    ph_print("[*] Copied to Clipboard")
else:
    with open(args.output + args.format, "w") as f:
        f.write(stager)
    if stager:
        ph_print("[*] Stager created successfully")
        exit(0)
    else:
        ph_print("[!] Could not create the payload")
        exit(1)
