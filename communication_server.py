import socket
import argparse
import time
import json

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

    print(f"[COMM] Listening on {args.recv_host}:{args.recv_port} for the computation server.")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((args.recv_host, args.recv_port))
    server_socket.listen(1)

    # Connect once to the receiver
    print(f"[COMM] Connecting once to the Receiver at {args.forward_host}:{args.forward_port}...")
    recv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    recv_socket.connect((args.forward_host, args.forward_port))
    print("[COMM] Single connection established with Receiver.")

    # Accept once from the computation server
    print("[COMM] Waiting for single TCP handshake with Computation Server...")
    comp_conn, comp_addr = server_socket.accept()
    print(f"[COMM] Single connection established with Computation Server at {comp_addr}")

    try:
        while True:
            # Continuously read jobs from computation server
            data = comp_conn.recv(65535)
            if not data:
                print("[COMM] Computation server closed the connection. Exiting loop.")
                break

            job = json.loads(data.decode("utf-8"))
            job_id = job.get('job_id')
            start_time = job.get('start_time', 0)
            print(f"[COMM] Received job {job_id}, start_time={start_time}")

            # Forward the job to the same receiver socket
            recv_socket.sendall(json.dumps(job).encode("utf-8"))

    except KeyboardInterrupt:
        print("\n[COMM] Ctrl+C caught. Shutting down.")
    finally:
        comp_conn.close()
        recv_socket.close()
        server_socket.close()

if __name__ == "__main__":
    main()
