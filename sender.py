import socket
import argparse
import json
import time
import csv
import random

def generate_batch(batch_size=5, matrix_size=200):
    """
    Generate a list of jobs to simulate CPU-bound tasks.
    Each job has:
      - job_id
      - matrix_size
    """
    jobs = []
    for i in range(batch_size):
        jobs.append({
            "job_id": i,
            "matrix_size": matrix_size
        })
    return jobs

def send_batch(jobs, server_ip, port):
    """
    Send a batch of jobs to the server, measure the round-trip time,
    and return (results, round_trip_time).
    """
    start_time = time.time()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((server_ip, port))
        s.sendall(json.dumps(jobs).encode("utf-8"))
        data = s.recv(65535)
    end_time = time.time()

    round_trip = end_time - start_time
    results = json.loads(data.decode("utf-8"))  # e.g. [{"job_id": 0, "status": "completed"}, ...]
    return results, round_trip

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server_ip", default="127.0.0.1", help="IP of the computation server")
    parser.add_argument("--port", type=int, default=5000, help="Port of the computation server")
    parser.add_argument("--num_batches", type=int, default=3, help="Number of batches to send")
    parser.add_argument("--batch_size", type=int, default=5, help="Number of jobs in each batch")
    parser.add_argument("--matrix_size", type=int, default=200, help="Matrix size for each job (NxN)")
    parser.add_argument("--min_delay", type=float, default=1.0, help="Min random delay (seconds) between batches")
    parser.add_argument("--max_delay", type=float, default=3.0, help="Max random delay (seconds) between batches")
    parser.add_argument("--csv_out", default="results.csv", help="CSV file to write results to")
    args = parser.parse_args()

    print(f"[SENDER] Will send {args.num_batches} batches, each with {args.batch_size} jobs.")
    print(f"[SENDER] Using matrix_size={args.matrix_size}. Random interval between {args.min_delay} and {args.max_delay} seconds.")

    # Prepare CSV
    with open(args.csv_out, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["batch_index", "job_id", "batch_rtt_seconds"])

        for batch_index in range(args.num_batches):
            jobs = generate_batch(batch_size=args.batch_size, matrix_size=args.matrix_size)
            
            print(f"[SENDER] Sending batch {batch_index+1}/{args.num_batches}...")
            results, rtt = send_batch(jobs, args.server_ip, args.port)

            print(f"[SENDER] Batch {batch_index+1} round-trip time: {rtt:.2f} s")
            # Log each job's measured round-trip time. We apply the same batch RTT to all jobs here,
            # as we're sending them in a single chunk and receiving a single chunk.
            for res in results:
                writer.writerow([batch_index, res["job_id"], rtt])

            # Wait a random interval before sending the next batch (except after the last batch).
            if batch_index < args.num_batches - 1:
                delay = random.uniform(args.min_delay, args.max_delay)
                print(f"[SENDER] Waiting {delay:.2f} s before next batch...")
                time.sleep(delay)

    print(f"[SENDER] All batches complete. Results saved to {args.csv_out}")

if __name__ == "__main__":
    main()
