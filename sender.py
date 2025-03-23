import socket
import argparse
import json
import time

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--comm_host", default="127.0.0.1",
                        help="Host/IP where the Communication Server is listening")
    parser.add_argument("--comm_port", type=int, default=5000,
                        help="Port of the Communication Server for sender")
    parser.add_argument("--num_jobs", type=int, default=5,
                        help="Number of jobs to send")
    args = parser.parse_args()

    print(f"[SENDER] Connecting once to Communication at {args.comm_host}:{args.comm_port} ...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((args.comm_host, args.comm_port))
    print("[SENDER] Single connection established with Communication Server.")

    time.sleep(5)

    for job_id in range(args.num_jobs):
        start_time = time.time()  # Record the 'start of job' (for E2E measurement)
        job = {
            "job_id": job_id,
            "start_time": start_time,
        }

        print(f"[SENDER] Sending job {job_id}, start_time={start_time:.4f}")
        s.sendall(json.dumps(job).encode("utf-8"))

        time.sleep(1)  # Optional delay between jobs

    print("[SENDER] All jobs sent. Closing the socket.")
    s.close()

if __name__ == "__main__":
    main()
