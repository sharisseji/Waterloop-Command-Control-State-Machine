# BUGGED FILE
import CommandControlSM
import logging
import test_pb2

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
# Enum for board types
BMS = 0
ST = 1
MC = 2

# Define the board types for easier reference
BOARD_TYPES = {
    BMS: "BMS",
    ST: "S&T",
    MC: "MC"
}

# Defining dictionaries for each board's data types
BMS_DATA_TYPES = {
    0: test_pb2.BMSDataType.TEMPERATURE_ADC,
    1: test_pb2.BMSDataType.AVG_TEMP_MUX,
    2: test_pb2.BMSDataType.TEMPERATURE_THERMISTOR,
    3: test_pb2.BMSDataType.AVG_THERMISTOR_TEMP_MUX,
    4: test_pb2.BMSDataType.MUX1_TEMP,
    5: test_pb2.BMSDataType.MUX2_TEMP,
    6: test_pb2.BMSDataType.MUX3_TEMP,
    7: test_pb2.BMSDataType.MUX4_TEMP,
    8: test_pb2.BMSDataType.MUX5_TEMP,
    9: test_pb2.BMSDataType.MUX6_TEMP
}

ST_DATA_TYPES = {
    0: test_pb2.STDataType.PRESSURE,
    1: test_pb2.STDataType.LIM_ONE_TEMP_ONE,
    2: test_pb2.STDataType.LIM_ONE_TEMP_TWO,
    3: test_pb2.STDataType.LIM_ONE_TEMP_THREE,
    4: test_pb2.STDataType.LIM_TWO_TEMP_ONE,
    5: test_pb2.STDataType.LIM_TWO_TEMP_TWO,
    6: test_pb2.STDataType.LIM_TWO_TEMP_THREE,
    7: test_pb2.STDataType.X_ACCEL,
    8: test_pb2.STDataType.Y_ACCEL,
    9: test_pb2.STDataType.X_GYRO,
    10: test_pb2.STDataType.Y_GYRO,
    11: test_pb2.STDataType.Z_GYRO
}

MC_DATA_TYPES = {
    0: test_pb2.MCDataType.BATTERY_VOLTAGE,
    1: test_pb2.MCDataType.BATTERY_CURRENT,
    2: test_pb2.MCDataType.SPEED,
    3: test_pb2.MCDataType.MOTOR_TEMP,
    4: test_pb2.MCDataType.DRIVING_DIRECTION,
    5: test_pb2.MCDataType.VOLTAGE,
    6: test_pb2.MCDataType.CURRENT,
    7: test_pb2.MCDataType.CTRL_TEMP
}

# Function to validate the CAN message length
def validate_can_message(msg):
    if len(msg.data) < 2 or len(msg.data) > 8:
        logger.error(f"Invalid CAN message length: {len(msg.data)}. Expected between 2 and 8 bytes.")
        # error_indication_led()
        return False
    return True

# Function to validate the board type and data type
def validate_data_type(board_type, data_type):
    if board_type not in [BMS, ST, MC]:
        logger.error(f"Invalid board type: {board_type}. Expected 0 (BMS), 1 (S&T), or 2 (MC).")
        return False
    if board_type == BMS and data_type not in BMS_DATA_TYPES:
        logger.error(f"Invalid data type for BMS: {data_type}.")
        return False
    elif board_type == ST and data_type not in ST_DATA_TYPES:
        logger.error(f"Invalid data type for S&T: {data_type}.")
        return False
    elif board_type == MC and data_type not in MC_DATA_TYPES:
        logger.error(f"Invalid data type for MC: {data_type}.")
        return False
    return True

# Function to process the CAN message and prepare it for gRPC
def process_CAN_message(msg):
    # Checking if it's valid CAN message
    if not validate_can_message(msg):
        return
    board_type = msg.data[0]  # Board type: 0 for BMS, 1 for S&T, 2 for MC
    data_type = msg.data[1]  # Data type specific to the board
    sensor_id = f"{board_type}_{data_type}"   # Create a sensor ID based on the board type and data type
    raw_data = msg.data[2:]
    # Checking if it's valid board type
    if not validate_data_type(board_type, data_type):
        return
    # Initialize the telemtry data message
    telemetry_data = generate_grpc.TelemetryData()
    telemetry_data.board_type = board_type
    telemetry_data.sensor_id = sensor_id
    telemetry_data.data = bytes(raw_data)
    # Handle BMS data types
    if board_type == BMS:
        bms_data_type = BMS_DATA_TYPES.get(data_type)
        if bms_data_type:
            telemetry_data.bms_data_type = bms_data_type
        else:
            logger.error(f"Unknown BMS Data Type: {data_type}")
            return
    # Handle ST data types
    elif board_type == ST:
        st_data_type = ST_DATA_TYPES.get(data_type)
        if st_data_type:
            telemetry_data.st_data_type = st_data_type
        else:
            logger.error(f"Unknown S&T Data Type: {data_type}")
            return
    # Handle MC data types
    elif board_type == MC:
        mc_data_type = MC_DATA_TYPES.get(data_type)
        if mc_data_type:
            telemetry_data.mc_data_type = mc_data_type
        else:
            logger.error(f"Unknown MC Data Type: {data_type}")
            return
    else:
        logger.error(f"Unknown board type: {board_type}")
        return
    # Send telemetry data via gRPC
    try:
        response = stub.SendTelemetry(telemetry_data)
        logger.info(f"Telemetry data sent: {response}")
    except grpc.RpcError as e:
        logger.error(f"Failed to send telemetry data: {e.details()}")

# Function to listen for CAN messages with a timeout
def listen_for_can_messages():
    """Listen for incoming CAN messages and process them."""
    logger.info("Listening for CAN messages...")
    while True:
        try:
            msg = BUS.recv(timeout = 1)  # 1 second timeout
            if msg is not None:
                logger.info(f"Received CAN message: ID={msg.arbitration_id}, Data={msg.data.hex()}")
                process_CAN_message(msg)
            else:
                logger.debug("No message received within the timeout period.")
        except can.CanError as e:
            logger.error(f"CAN error: {e}")
            break
    # Function to check the health of the STM-32's
