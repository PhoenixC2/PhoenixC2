#! /usr/bin/env python3

from Utils import *
import Creator
import os
import clipboard
curr_dir = os.getcwd()
# os.chdir("/usr/share/phoenix-framework")

ph_print(logo)

parser = ArgumentParser(
    "pfcreate", description="Create Stagers to interact with the chosen listener.")
parser.add_argument("-st", "--stager", help="Use an existing stager.", metavar="Stager")
parser.add_argument("-l", "--listener", help="The Listener to use", metavar="Listener")
parser.add_argument("-f", "--format", help="The Format to use", default=".py", metavar="Format")
parser.add_argument("-e", "--encoder",
                    help="The Encoder to use", default="base64", metavar="Encoder")
parser.add_argument("-n", "--name", help="The Name of the Stager", metavar="Name")
parser.add_argument("-t", "--timeout",
                    help="How often the Stager should try to connect before exiting", default=5000, metavar="Timeout", type=int)
parser.add_argument("-d", "--delay", help="How long to wait before starting the Stager", default=1, metavar="Delay", type=int)
parser.add_argument("-r", "--random", help="Randomize the size of the payload", action="store_true")
parser.add_argument(
    "-o", "--output", help="The output file", default="payload", metavar="File")
parser.add_argument(
    "-c", "--copy", help="Copy the payload to the clipboard", action="store_true")
parser.add_argument("-s", "--show", help="Show the Options of an Argument", metavar="Category")

args = parser.parse_args()

if args.show:
    if args.show == "listeners":
        ph_print("Listeners:")
        curr.execute("SELECT * FROM Listeners")
        listeners = curr.fetchall()
        if not listeners:
            ph_print("No Listeners found")
        for listener in listeners:
            ph_print(f"({listener[0]}) {listener[1]} [{listener[2]}]")
    elif args.show == "stagers":
        ph_print("Stagers:")
        curr.execute("SELECT * FROM Stagers")
        stagers = curr.fetchall()
        if not stagers:
            ph_print("No Stagers found")
        for stager in stagers:
            ph_print(f"({stager[0]}) {stager[1]} [{stager[2]}]")
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
if not args.listener and not args.stager:
    ph_print("No Listener specified")
    exit(0)
if (not args.name and not args.stager) or (args.name == "" and not args.stager):
    ph_print("No Name specified")
    exit(0)
if args.encoder not in Creator.encoders:
    ph_print(f"[!] Unknown Encoder: {args.encoder}", alert="error")
    exit(1)
if args.format not in Creator.formats:
    ph_print(f"[!] Unknown Format: {args.format}", alert="error")
    exit(1)
ph_print("[*] Creating Stager")
output = args.output + args.format if not args.copy else "Clipboard"
ph_print("[*] Output: " + output)

# Create the Payload
try:
    stager = Creator.create_stager(args.listener, args.encoder, args.random, args.timeout, args.stager, args.name, args.format, args.delay)
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
