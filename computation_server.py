import socket
import argparse
import json
import time
import numpy as np

def perform_matrix_multiplication(n=200):
    """
    Perform a random NxN matrix multiplication using numpy,
    simulating a CPU-intensive task on the computation server.
    """
    A = np.random.rand(n, n)
    B = np.random.rand(n, n)
    C = A @ B  # matrix multiply
    return float(np.sum(C))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--comm_host", default="127.0.0.1",
                        help="Host/IP of the communication server")
    parser.add_argument("--comm_port", type=int, default=6000,
                        help="Port of the communication server")
    parser.add_argument("--matrix_size", type=int, default=200,
                        help="Matrix dimension for NxN multiplication")
    args = parser.parse_args()

    print(f"[COMPUTATION] Connecting once to Communication at {args.comm_host}:{args.comm_port} ...")
    comp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    comp_socket.connect((args.comm_host, args.comm_port))
    print("[COMPUTATION] Single connection established with Communication Server.")

    try:
        while True:
            # Continuously read jobs from the communication server
            data = comp_socket.recv(65535)
            if not data:
                print("[COMPUTATION] Communication server closed connection. Exiting.")
                break

            job = json.loads(data.decode("utf-8"))
            job_id = job.get("job_id", -1)
            start_time = job.get("start_time", None)

            # Perform CPU-intensive work
            _ = perform_matrix_multiplication(args.matrix_size)

            # Now send the job back to the Communication Server
            # so it can be forwarded to the Receiver
            comp_socket.sendall(json.dumps(job).encode("utf-8"))
            print(f"[COMPUTATION] Completed job {job_id} and sent it back.")

    except KeyboardInterrupt:
        print("\n[COMPUTATION] Ctrl+C caught, shutting down.")
    finally:
        comp_socket.close()

if __name__ == "__main__":
    main()
