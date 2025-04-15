echo "--- Starting Computation Server ---"

# --- Configuration ---
COMP_UPLINK_TRACE="mm-link_output/constant_1mbps.trace" # Ensure valid trace!
COMP_DOWNLINK_TRACE="mm-link_output/constant_1mbps.trace" # Ensure valid trace!
COMP_DELAY_MS=5
COMP_PORT=6000
PYTHON_SCRIPT="computation_server.py"
MATRIX_SIZE=3
OUTER_IP_FILE="/tmp/comp_outer_ip.txt"
INNER_IP_FILE="/tmp/comp_inner_ip.txt"
INNER_SCRIPT_FILE="/tmp/comp_inner_script.sh"
COMM_IP_FILE="/tmp/comm_outer_ip.txt"
# --- End Configuration ---

rm -f "$OUTER_IP_FILE" "$INNER_IP_FILE" "$INNER_SCRIPT_FILE"

# Export variables needed by inner script
export COMP_PORT PYTHON_SCRIPT INNER_IP_FILE MATRIX_SIZE
# Define and export IP function
get_mahimahi_ip() { ip -4 addr show scope global | grep -Eo 'inet ([0-9]{1,3}\.){3}[0-9]{1,3}' | awk '{print $2}' | head -n 1; }
export -f get_mahimahi_ip

# Start outer shell
# mm-link *DOES* use --
mm-link "$COMP_UPLINK_TRACE" "$COMP_DOWNLINK_TRACE" -- bash -c '
  # Inside Outer Shell (mm-link)
  OUTER_IP=$(get_mahimahi_ip)
  if [ -z "$OUTER_IP" ]; then echo "Error: Failed to get Comp Outer IP."; exit 1; fi
  echo "Comp Server Outer IP: $OUTER_IP"
  echo "$OUTER_IP" > "'$OUTER_IP_FILE'"

  echo "Waiting for Communication Server Outer IP file ($COMM_IP_FILE)..."
  while [ ! -f "'$COMM_IP_FILE'" ]; do sleep 1; done
  COMM_HOST=$(cat "'$COMM_IP_FILE'")
  export COMM_HOST # Export COMM_HOST for the inner script
  echo "Found Communication Server Outer IP: $COMM_HOST"

  # Create inner script
  cat << EOF > "'$INNER_SCRIPT_FILE'"
#!/bin/bash
# Script for Inner Shell (mm-delay)
export PATH=\$PATH

# Redefine function locally for robustness
get_mahimahi_ip() {
  # Use single quotes for awk script
  ip -4 addr show scope global | grep -Eo "inet ([0-9]{1,3}\.){3}[0-9]{1,3}" | awk '\''{print \$2}'\'' | head -n 1
}

INNER_IP=\$(get_mahimahi_ip)
if [ -z "\$INNER_IP" ]; then echo "Error: Failed to get Comp Inner IP."; exit 1; fi
echo "Comp Server Inner IP: \$INNER_IP"; echo "\$INNER_IP" > "\$INNER_IP_FILE"

echo "Starting Python server, connecting to Comm Server \$COMM_HOST:\$COMP_PORT..."
python3 "\$PYTHON_SCRIPT" --comm_host="\$COMM_HOST" --comm_port="\$COMP_PORT" --matrix_size="\$MATRIX_SIZE" &
PYTHON_PID=\$!
echo "Comp Server Python server PID: \$PYTHON_PID"
wait \$PYTHON_PID
echo "Comp Server Python server exited."
rm -f "\$INNER_IP_FILE"
EOF
  chmod +x "'$INNER_SCRIPT_FILE'"

  echo "Starting inner shell by executing $INNER_SCRIPT_FILE ..."
  # mm-delay does *NOT* use --
  mm-delay "'$COMP_DELAY_MS'" /bin/bash "'$INNER_SCRIPT_FILE'" &
  INNER_SHELL_PID=$!
  echo "Inner shell PID: $INNER_SHELL_PID (running $INNER_SCRIPT_FILE)"

  echo "Waiting for Inner IP file ($INNER_IP_FILE)..."
  while [ ! -f "$INNER_IP_FILE" ]; do
    if ! kill -0 $INNER_SHELL_PID 2>/dev/null; then echo "Error: Inner shell exited prematurely."; rm -f "'$OUTER_IP_FILE'" "'$INNER_SCRIPT_FILE'"; exit 1; fi
    sleep 0.5
  done
  INNER_IP_FOR_IPTABLES=$(cat "$INNER_IP_FILE")
  # Basic validation
  if ! [[ "$INNER_IP_FOR_IPTABLES" =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
      echo "Error: Invalid Inner IP read from file: $INNER_IP_FOR_IPTABLES"
      rm -f "'$OUTER_IP_FILE'" "'$INNER_SCRIPT_FILE'"
      exit 1
  fi
  echo "Got Inner IP: $INNER_IP_FOR_IPTABLES"

  echo "Enabling IP forwarding and setting up iptables in outer shell ($OUTER_IP)..."
  sudo sysctl -w net.ipv4.ip_forward=1
  sudo iptables -t nat -A PREROUTING -p tcp --dport "$COMP_PORT" -j DNAT --to-destination "$INNER_IP_FOR_IPTABLES":"$COMP_PORT"
  sudo iptables -A FORWARD -p tcp -d "$INNER_IP_FOR_IPTABLES" --dport "$COMP_PORT" -j ACCEPT
  sudo iptables -t nat -A POSTROUTING -p tcp -d "$INNER_IP_FOR_IPTABLES" --dport "$COMP_PORT" -j MASQUERADE

  echo "iptables rules set. Comp Server setup complete. Outer shell waiting..."
  wait $INNER_SHELL_PID
  echo "Comp Server outer shell finished."
  rm -f "'$OUTER_IP_FILE'" "'$INNER_SCRIPT_FILE'"
' &

echo "Computation Server script launched in background."
