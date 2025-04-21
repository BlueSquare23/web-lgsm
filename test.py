import os
import sys
import signal

DEBUG=True
HOST='0.0.0.0'
PORT=5000

def signalint_handler(sig, frame):
    # Suppress stderr for debug ctrl + c stack trace.
    with open(os.devnull, "w") as fnull:
        sys.stdout = fnull
        sys.stderr = fnull
        sys.stdout = sys.__stdout__
        print("\r [!] Ctrl + C received. Shutting down...")

    exit(0)

def start_debug():
    """Starts the app in debug mode"""
    from app import main
    if DEBUG:
        os.environ["DEBUG"] = "YES"

    # For clean ctrl + c handling.
    signal.signal(signal.SIGINT, signalint_handler)
    app = main()
    app.run(debug=True, host=HOST, port=PORT)

if __name__ == '__main__':
    start_debug()
