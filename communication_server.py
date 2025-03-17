import socket
import argparse
import time
import json

def forward_to_receiver(job, receiver_host, receiver_port):
    """
    Connect to the receiver server (which is in the MahiMahi shell),
    send the job, then close.
    """

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--recv_host", default="0.0.0.0",
                        help="Host/IP to bind for receiving jobs from computation_server")
    parser.add_argument("--recv_port", type=int, default=6000,
                        help="Port for receiving jobs from computation_server")
    parser.add_argument("--forward_host", default="127.0.0.1",
                        help="Host/IP of the receiver server")
    parser.add_argument("--forward_port", type=int, default=7000,
                        help="Port of the receiver server")
    args = parser.parse_args()

    print(f"[COMMUNICATION] Listening on {args.recv_host}:{args.recv_port}")
    print(f"[COMMUNICATION] Forwarding jobs to receiver at {args.forward_host}:{args.forward_port}")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((args.recv_host, args.recv_port))
    server_socket.listen(5)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((args.forward_host, args.forward_port))

    try:
        while True:
            print("[COMMUNICATION] Waiting for job from computation server...")
            conn, addr = server_socket.accept()
            print(f"[COMMUNICATION] Connected by {addr}")

            data = conn.recv(65535)
            if not data:
                conn.close()
                continue

            # One job at a time
            job = json.loads(data.decode("utf-8"))
            job_id = job.get('job_id')
            print(f"[COMMUNICATION] Received job {job_id} with start_time={job.get('start_time')}")
            recv_time = time.time()
            print(f"Time to receive on communication: {(recv_time - job.get('start_time')) * 1000} ms")
            print(f"Receive time: {recv_time}")
            
            # Forward the job (FIFO pass-through)
            # forward_to_receiver('1', args.forward_host, args.forward_port)
            s.sendall(json.dumps(job).encode("utf-8"))
            print("[COMMUNICATION] Job forwarded to receiver.")

            conn.close()

    except KeyboardInterrupt:
        print("\n[COMMUNICATION] Shutting down.")
    finally:
        server_socket.close()
        s.close()

if __name__ == "__main__":
    main()
