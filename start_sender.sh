echo "--- Starting Sender ---"

# --- Configuration ---
SENDER_UPLINK_TRACE="mm-link_output/constant_1mbps.trace" # Ensure valid trace!
SENDER_DOWNLINK_TRACE="mm-link_output/constant_1mbps.trace" # Ensure valid trace!
SENDER_DELAY_MS=5
COMM_PORT=5000 # Port connecting to Comm server
NUM_JOBS=5
PYTHON_SCRIPT="sender.py"
COMM_IP_FILE="/tmp/comm_outer_ip.txt" # Depends on Comm server Outer IP
# --- End Configuration ---

# Wait for the communication server IP file
echo "Waiting for Communication Server Outer IP file ($COMM_IP_FILE)..."
while [ ! -f $COMM_IP_FILE ]; do sleep 1; done
COMM_HOST=$(cat $COMM_IP_FILE)
echo "Found Communication Server Outer IP: $COMM_HOST"

echo "Starting sender process inside Mahimahi shells..."
# Note: mm-link uses "--", but mm-delay does not.
mm-link "$SENDER_UPLINK_TRACE" "$SENDER_DOWNLINK_TRACE" -- mm-delay "$SENDER_DELAY_MS" python3 "$PYTHON_SCRIPT" --comm_host="$COMM_HOST" --comm_port="$COMM_PORT" --num_jobs="$NUM_JOBS"

echo "Sender finished."
