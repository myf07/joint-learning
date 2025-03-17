import socket
import argparse
import json
import time

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0", help="Host/IP to bind the receiver")
    parser.add_argument("--port", type=int, default=7000, help="Port to listen on")
    args = parser.parse_args()

    print(f"[RECEIVER] Starting on {args.host}:{args.port}")

    receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    receiver_socket.bind((args.host, args.port))
    receiver_socket.listen(5)
    print("[RECEIVER] Waiting for job...")
    conn, addr = receiver_socket.accept()
    print(f"[RECEIVER] Connection from {addr}")

    try:
        while True:
            data = conn.recv(65535)
            if not data:
                conn.close()
                continue

            # Expecting a single job (JSON)
            # job = json.loads(data.decode("utf-8"))
            # job_id = job.get("job_id", "unknown")
            # start_time = job.get("start_time", None)
            
            end_time = time.time()
            print(f"End time: {end_time}")
            # if start_time is not None:
            #     elapsed_ms = (end_time - start_time) * 1000
            #     print(f"[RECEIVER] Job {job_id} end-to-end time: {elapsed_ms:.2f} ms")
            # else:
            #     print(f"[RECEIVER] Job {job_id} missing start_time, cannot calculate E2E")

            conn.close()

    except KeyboardInterrupt:
        print("\n[RECEIVER] Shutting down.")
    finally:
        receiver_socket.close()

if __name__ == "__main__":
    main()
