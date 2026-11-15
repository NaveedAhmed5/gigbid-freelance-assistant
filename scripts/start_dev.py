#!/usr/bin/env python3
"""GigBid Real-Time Full-Stack Local Launcher.

Starts all three core services concurrently:
1. GigSim Marketplace Simulator (Port 8001)
2. GigBid FastAPI REST & SSE Backend (Port 8000)
3. GigBid Next.js 14 Web Frontend (Port 3000)

Handles clean shutdown on Ctrl+C.
"""

import os
import subprocess
import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
WEB_DIR = ROOT_DIR / "apps" / "web"


def print_banner():
    print("=" * 80)
    print("           GIGBID REAL-TIME SYSTEM LAUNCHER           ".center(80))
    print("=" * 80)
    print("\nStarting all services in real time:")
    print("  1. GigSim Simulator API  -> http://localhost:8001")
    print("  2. GigBid FastAPI Backend -> http://localhost:8000")
    print("  3. GigBid Next.js Web UI  -> http://localhost:3000")
    print("\nPreloaded Reviewer Credentials:")
    print("  Email   : reviewer@gigbid.ai")
    print("  Password: reviewer-demo-pass")
    print("\nPress Ctrl+C at any time to shut down all services.")
    print("=" * 80 + "\n")


def main():
    print_banner()

    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT_DIR)

    processes = []

    try:
        # 1. Start GigSim Simulator on Port 8001
        print(">>> [1/3] Starting GigSim Marketplace Simulator on http://localhost:8001 ...")
        p_gigsim = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "gigsim.main:app", "--port", "8001", "--host", "127.0.0.1"],
            cwd=str(ROOT_DIR),
            env=env,
        )
        processes.append(("GigSim Simulator (8001)", p_gigsim))
        time.sleep(1.5)

        # 2. Start GigBid FastAPI Backend on Port 8000
        print(">>> [2/3] Starting GigBid FastAPI Backend on http://localhost:8000 ...")
        p_api = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "apps.api.main:app", "--port", "8000", "--host", "127.0.0.1", "--reload"],
            cwd=str(ROOT_DIR),
            env=env,
        )
        processes.append(("FastAPI Backend (8000)", p_api))
        time.sleep(1.5)

        # 3. Start Next.js Frontend on Port 3000
        print(">>> [3/3] Starting Next.js Web Frontend on http://localhost:3000 ...")
        # On Windows, npm is npm.cmd
        npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
        p_web = subprocess.Popen(
            [npm_cmd, "run", "dev"],
            cwd=str(WEB_DIR),
            env=env,
        )
        processes.append(("Next.js Web (3000)", p_web))

        print("\n" + "#" * 80)
        print("ALL SERVICES ARE NOW LIVE!")
        print("Open your browser and navigate to:")
        print("  --> http://localhost:3000 (GigBid Web Application)")
        print("  --> http://localhost:8000/docs (Interactive Swagger API Docs)")
        print("  --> http://localhost:8001/docs (GigSim Simulator API Docs)")
        print("#" * 80 + "\n")

        # Keep running and monitor processes
        while True:
            for name, proc in processes:
                poll = proc.poll()
                if poll is not None:
                    print(f"WARNING: Service '{name}' exited unexpectedly with code {poll}.")
            time.sleep(2)

    except KeyboardInterrupt:
        print("\n>>> Shutting down all GigBid services...")
    finally:
        for name, proc in processes:
            print(f"Terminating {name}...")
            try:
                proc.terminate()
                proc.wait(timeout=3)
            except Exception:
                proc.kill()
        print("All services stopped.")


if __name__ == "__main__":
    main()
