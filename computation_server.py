import socket
import argparse
import json
import time
import numpy as np

def perform_matrix_multiplication(n=200):
    """
    Perform a random NxN matrix multiplication using NumPy,
    simulating a CPU-intensive task.
    """
    print(f"Matrix size: {n}")
    A = np.random.rand(n, n)
    B = np.random.rand(n, n)
    C = A @ B  # matrix multiply
    return float(np.sum(C))  # Just return something to confirm the work was done

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

    print(f"[COMPUTATION] Will generate and send {args.num_jobs} jobs. Using matrix_size={args.matrix_size}")

    for job_id in range(args.num_jobs):
        # 1) Record start time (for E2E measurement)
        start_time = time.time()

        # 2) Perform CPU-intensive work
        # _ = perform_matrix_multiplication(args.matrix_size)

        # 3) Prepare job data
        job = {
            "job_id": job_id,
            "start_time": start_time,
        }

        comp_finished_time = time.time()
        print(f"Time to compute: {(comp_finished_time - start_time) * 1000} ms")
        print(f"Computation finished time: {comp_finished_time}")

        print(f"[COMPUTATION] Sending job {job_id}, start_time={start_time:.4f}")
        # 4) Send job to communication server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((args.comm_host, args.comm_port))
            s.sendall(json.dumps(job).encode("utf-8"))

        time.sleep(1)  # optional pause between jobs

    print("[COMPUTATION] All jobs sent. Exiting.")

if __name__ == "__main__":
    main()

# Build new server structure with mm-link parameters:
# UPLINK = wired300
# DOWNLINK = wired12

# Commands
# RECV: python3 receiver.py --host=0.0.0.0 --port=7000
# COMM: python3 communication_server.py --recv_host=0.0.0.0 --recv_port=6000 --forward_host=10.0.0.2 --forward_port=7000
# COMP: python3 computation_server.py --comm_host=127.0.0.1 --comm_port=6000 --num_jobs=5 --matrix_size=3
