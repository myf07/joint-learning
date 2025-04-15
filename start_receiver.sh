echo "--- Starting Receiver ---"

# --- Configuration ---
RECEIVER_UPLINK_TRACE="mm-link_output/constant_1mbps.trace" # Ensure valid trace!
RECEIVER_DOWNLINK_TRACE="mm-link_output/constant_1mbps.trace" # Ensure valid trace!
RECEIVER_DELAY_MS=20
RECEIVER_PORT=7000
PYTHON_SCRIPT="receiver.py"
OUTER_IP_FILE="/tmp/receiver_outer_ip.txt"
INNER_IP_FILE="/tmp/receiver_inner_ip.txt"
INNER_SCRIPT_FILE="/tmp/receiver_inner_script.sh"
# --- End Configuration ---

# Clean up previous temp files
rm -f "$OUTER_IP_FILE" "$INNER_IP_FILE" "$INNER_SCRIPT_FILE"

# Export variables needed by the inner script
export RECEIVER_PORT PYTHON_SCRIPT INNER_IP_FILE
# Define function to get IP (more robust)
get_mahimahi_ip() {
  # Get first global IPv4 address
  ip -4 addr show scope global | grep -Eo 'inet ([0-9]{1,3}\.){3}[0-9]{1,3}' | awk '{print $2}' | head -n 1
}
# Export function - best effort, redefined in inner script for safety
export -f get_mahimahi_ip

# Start the outer mm-link shell
# mm-link *DOES* use --
mm-link "$RECEIVER_UPLINK_TRACE" "$RECEIVER_DOWNLINK_TRACE" -- bash -c '
  # Inside Outer Shell (mm-link)
  OUTER_IP=$(get_mahimahi_ip)
  if [ -z "$OUTER_IP" ]; then
      echo "Error: Failed to get Receiver Outer IP. mm-link failed? Check trace files."
      exit 1
  fi
  echo "Receiver Outer IP: $OUTER_IP"
  echo "$OUTER_IP" > "'$OUTER_IP_FILE'"

  # Create the script for the inner shell
  cat << EOF > "'$INNER_SCRIPT_FILE'"
#!/bin/bash
# Script for Inner Shell (mm-delay)
export PATH=\$PATH

# Redefine function locally for robustness
get_mahimahi_ip() {
  # Use single quotes for awk script to prevent premature $ expansion
  # This ensures the inner shell executes awk '\''{print $2}'\''
  ip -4 addr show scope global | grep -Eo "inet ([0-9]{1,3}\.){3}[0-9]{1,3}" | awk '\''{print \$2}'\'' | head -n 1
}

INNER_IP=\$(get_mahimahi_ip)
if [ -z "\$INNER_IP" ]; then
    echo "Error: Failed to get Receiver Inner IP."
    exit 1
fi
echo "Receiver Inner IP: \$INNER_IP" # Should now echo only the IP
echo "\$INNER_IP" > "\$INNER_IP_FILE"

echo "Starting Python server on 0.0.0.0:\$RECEIVER_PORT..."
python3 "\$PYTHON_SCRIPT" --host=0.0.0.0 --port="\$RECEIVER_PORT" &
PYTHON_PID=\$!
echo "Receiver Python server PID: \$PYTHON_PID"
wait \$PYTHON_PID
echo "Receiver Python server exited."
rm -f "\$INNER_IP_FILE"
EOF

  chmod +x "'$INNER_SCRIPT_FILE'"

  echo "Starting inner shell by executing $INNER_SCRIPT_FILE ..."
  # mm-delay does *NOT* use --
  mm-delay "'$RECEIVER_DELAY_MS'" /bin/bash "'$INNER_SCRIPT_FILE'" &
  INNER_SHELL_PID=$!
  echo "Inner shell PID: $INNER_SHELL_PID (running $INNER_SCRIPT_FILE)"

  echo "Waiting for Inner IP file ($INNER_IP_FILE)..."
  while [ ! -f "$INNER_IP_FILE" ]; do
      if ! kill -0 $INNER_SHELL_PID 2>/dev/null; then
          echo "Error: Inner shell exited prematurely. Cannot get Inner IP."
          rm -f "'$OUTER_IP_FILE'" "'$INNER_SCRIPT_FILE'"
          exit 1
      fi
      sleep 0.5
  done
  # Read the IP (which should now be clean)
  INNER_IP_FOR_IPTABLES=$(cat "$INNER_IP_FILE")
  # Basic validation that it looks like an IP
  if ! [[ "$INNER_IP_FOR_IPTABLES" =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
      echo "Error: Invalid Inner IP read from file: $INNER_IP_FOR_IPTABLES"
      rm -f "'$OUTER_IP_FILE'" "'$INNER_SCRIPT_FILE'"
      # Optionally kill the inner shell if needed: kill $INNER_SHELL_PID
      exit 1
  fi
  echo "Got Inner IP: $INNER_IP_FOR_IPTABLES"

  echo "Enabling IP forwarding and setting up iptables in outer shell ($OUTER_IP)..."
  sudo sysctl -w net.ipv4.ip_forward=1
  # Use the validated IP in iptables commands
  sudo iptables -t nat -A PREROUTING -p tcp --dport "$RECEIVER_PORT" -j DNAT --to-destination "$INNER_IP_FOR_IPTABLES":"$RECEIVER_PORT"
  sudo iptables -A FORWARD -p tcp -d "$INNER_IP_FOR_IPTABLES" --dport "$RECEIVER_PORT" -j ACCEPT
  sudo iptables -t nat -A POSTROUTING -p tcp -d "$INNER_IP_FOR_IPTABLES" --dport "$RECEIVER_PORT" -j MASQUERADE

  echo "iptables rules set. Receiver setup complete. Outer shell waiting for inner shell ($INNER_SHELL_PID)..."
  wait $INNER_SHELL_PID
  echo "Receiver outer shell finished."
  rm -f "'$OUTER_IP_FILE'" "'$INNER_SCRIPT_FILE'"
' &

echo "Receiver script launched in background."
