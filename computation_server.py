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
    parser.add_argument("--num_jobs", type=int, default=3,
                        help="Number of jobs to generate and send")
    parser.add_argument("--matrix_size", type=int, default=200,
                        help="Matrix dimension for NxN multiplication")
    args = parser.parse_args()

    print(f"[COMPUTATION] Will compute & send {args.num_jobs} jobs, matrix_size={args.matrix_size}")
    print(f"[COMPUTATION] Connecting once to Communication at {args.comm_host}:{args.comm_port} ...")

    # Single persistent connection
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((args.comm_host, args.comm_port))
    print("[COMPUTATION] Single connection established with Communication Server.")

    time.sleep(5)

    for job_id in range(args.num_jobs):
        # Record start time if you want end-to-end to include compute
        start_time = time.time()

        # CPU-intensive work
        _ = perform_matrix_multiplication(args.matrix_size)

        job = {
            "job_id": job_id,
            "start_time": start_time,
        }

        print(f"[COMPUTATION] Sending job {job_id}, start_time={start_time:.4f}")
        s.sendall(json.dumps(job).encode("utf-8"))

        time.sleep(1)  # optional pause between jobs

    print("[COMPUTATION] All jobs sent. Closing the socket.")
    s.close()

if __name__ == "__main__":
    main()
