# LDOS - Yifan Ma's Joint Learning project

## Commands to run each server
RECV: python3 receiver.py --host=0.0.0.0 --port=7000

COMM: python3 communication_server.py --recv_host=0.0.0.0 --recv_port=6000 --forward_host=10.0.0.2 --forward_port=7000

COMP: python3 computation_server.py --comm_host=127.0.0.1 --comm_port=6000 --num_jobs=5 --matrix_size=3

## Building new server structure with mm-link parameters
UPLINK = wired300

DOWNLINK = wired12

## TODO
- Remove the extra TCP/IP 3-way handshake
- Setup servers to properly do the round trip communication timing
