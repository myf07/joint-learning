# LDOS - Yifan Ma's Joint Learning Project

## Commands for running each server
First, start **SEND**, **RECV**, and **COMP** inside `mm-delay` shells.

**Then, start the servers in the order below:**

**RECV**: `python3 receiver.py --host=0.0.0.0 --port=7000`

**COMM**: `python3 communication_server.py --sender_port=5000 --comp_port=6000 --receiver_host=10.0.0.2 --receiver_port=7000`

**COMP**: `python3 computation_server.py --comm_host=10.0.0.3 --comm_port=6000 --matrix_size=3`

**SEND**: `python3 sender.py --comm_host=10.0.0.5 --comm_port=5000 --num_jobs=5`

*Note*: For **COMM**, **COMP**, **SEND**, use `ip addr show` to find the peer address, and use that for the host address.

## Building new server structure with mm-link parameters
`UPLINK = wired300`

`DOWNLINK = wired12`

## TODO

- Debug the scripts
- Check end-to-end time
- Create single script with tmux
- Check end-to-end time
- Create random data to buffer packet size
- Check end-to-end time
- Add job scheduling on computation server
- Check end-to-end time
- Add packet scheduling for communication server
