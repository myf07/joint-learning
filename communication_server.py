import socket
import argparse
import json
import time

def main():
    parser = argparse.ArgumentParser()
    # 1) Listen for the Sender
    parser.add_argument("--sender_host", default="0.0.0.0",
                        help="Host/IP to bind for receiving jobs from the Sender")
    parser.add_argument("--sender_port", type=int, default=5000,
                        help="Port for receiving jobs from the Sender")

    # 2) Listen for the Computation Server
    parser.add_argument("--comp_host", default="0.0.0.0",
                        help="Host/IP to bind for the Computation server")
    parser.add_argument("--comp_port", type=int, default=6000,
                        help="Port for the Computation server")

    # 3) Connect once to the Receiver
    parser.add_argument("--receiver_host", default="127.0.0.1",
                        help="Host/IP of the receiver server")
    parser.add_argument("--receiver_port", type=int, default=7000,
                        help="Port of the receiver server")

    args = parser.parse_args()

    print(f"[COMM] 1) Listening on {args.sender_host}:{args.sender_port} for the Sender.")
    sender_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sender_socket.bind((args.sender_host, args.sender_port))
    sender_socket.listen(1)

    print(f"[COMM] 2) Listening on {args.comp_host}:{args.comp_port} for the Computation Server.")
    comp_listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    comp_listen_socket.bind((args.comp_host, args.comp_port))
    comp_listen_socket.listen(1)

    print(f"[COMM] 3) Connecting once to Receiver at {args.receiver_host}:{args.receiver_port}...")
    receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    receiver_socket.connect((args.receiver_host, args.receiver_port))
    print("[COMM] Single connection established with Receiver.")

    print("[COMM] Accepting single handshake from Computation Server...")
    comp_conn, comp_addr = comp_listen_socket.accept()
    print(f"[COMM] Connected with Computation Server at {comp_addr}")

    print("[COMM] Accepting single handshake from Sender...")
    sender_conn, sender_addr = sender_socket.accept()
    print(f"[COMM] Connected with Sender at {sender_addr}")

    try:
        while True:
            # 1) Read next job from the Sender
            data = sender_conn.recv(65535)
            if not data:
                print("[COMM] Sender closed connection. Exiting loop.")
                break

            job = json.loads(data.decode("utf-8"))
            job_id = job.get("job_id")
            print(f"[COMM] Received job {job_id} from Sender.")

            # 2) Forward the job to Computation
            comp_conn.sendall(json.dumps(job).encode("utf-8"))
            print(f"[COMM] Sent job {job_id} to Computation Server.")

            # 3) Wait for Computation to send the completed job back
            comp_data = comp_conn.recv(65535)
            if not comp_data:
                print("[COMM] Computation server closed connection. Exiting loop.")
                break

            completed_job = json.loads(comp_data.decode("utf-8"))
            cjob_id = completed_job.get("job_id")
            print(f"[COMM] Received completed job {cjob_id} from Computation.")

            # 4) Forward the completed job to Receiver
            receiver_socket.sendall(json.dumps(completed_job).encode("utf-8"))
            print(f"[COMM] Forwarded job {cjob_id} to Receiver.\n")

    except KeyboardInterrupt:
        print("\n[COMM] Ctrl+C caught. Shutting down.")
    finally:
        sender_conn.close()
        comp_conn.close()
        sender_socket.close()
        comp_listen_socket.close()
        receiver_socket.close()

if __name__ == "__main__":
    main()
