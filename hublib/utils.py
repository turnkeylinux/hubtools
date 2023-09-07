import sys

def fatal(e):
    print("error: " + str(e), file=sys.stderr)
    sys.exit(1)
