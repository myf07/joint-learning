# LDOS - Yifan Ma's Joint Learning project

## Commands to run each server
First, start **RECV** and **COMP** inside `mm-delay` shells.

**RECV**: `python3 receiver.py --host=0.0.0.0 --port=7000`

**COMM**: `python3 communication_server.py --recv_host=0.0.0.0 --recv_port=6000 --forward_host=10.0.0.2 --forward_port=7000`

**COMP**: `python3 computation_server.py --comm_host=10.0.0.3 --comm_port=6000 --num_jobs=5 --matrix_size=3`

*Note*: For **COMP**, use `ip addr show` to find the peer address, and use that for `comm_host`.

## Building new server structure with mm-link parameters
`UPLINK = wired300`

`DOWNLINK = wired12`

## TODO
- Setup servers to properly do the round trip communication timing
