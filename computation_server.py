import socket
import argparse
import json
import numpy as np

def perform_matrix_multiplication(n=200):
    """
    Perform a random NxN matrix multiplication using NumPy,
    simulating a CPU-intensive task.
    """
    A = np.random.rand(n, n)
    B = np.random.rand(n, n)
    C = A @ B  # matrix multiply
    return float(np.sum(C))  # Just return something to confirm the work was done

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0",
                        help="Host/IP on which to bind the server")
    parser.add_argument("--port", type=int, default=5000,
                        help="Port to listen on")
    args = parser.parse_args()

    print(f"[COMPUTATION SERVER] Starting on {args.host}:{args.port}")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((args.host, args.port))
    server_socket.listen(5)

    try:
        while True:
            print("[COMPUTATION SERVER] Waiting for connection...")
            conn, addr = server_socket.accept()
            print(f"[COMPUTATION SERVER] Connection established from {addr}")

            data = conn.recv(65535)
            if not data:
                conn.close()
                continue

            jobs = json.loads(data.decode("utf-8"))  # e.g. [{"job_id": 0, "matrix_size": 200}, ...]

            results = []
            for job in jobs:
                job_id = job["job_id"]
                matrix_size = job.get("matrix_size", 200)
                _ = perform_matrix_multiplication(matrix_size)
                results.append({
                    "job_id": job_id,
                    "status": "completed"
                })

            # Send back JSON results
            conn.sendall(json.dumps(results).encode("utf-8"))
            conn.close()
            print("[COMPUTATION SERVER] Batch processed and response sent.")

    except KeyboardInterrupt:
        print("\n[COMPUTATION SERVER] Shutting down.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()


# Build new server structure with mm-link parameters:
# UPLINK = wired300
# DOWNLINK = wired12
