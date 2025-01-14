import can  # use can.message()
import grpc
import test_pb2
import grpc_client  # client file that has test_pb2_gprc imported
import struct
import logging
import time

# SET UP
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)  # i'm assuming this is so you can test it?

# Initialization of gRPC channel and stub
channel = grpc.insecure_channel('') # use computer IP address instead of localhost:50051
# stub goes here, e


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

# Define a gRPC message object (example)
class GRPCMessage:
    def __init__(self, board_type, data_type, sensor_id, raw_data):  # change name of these fields later
        self.board_type = board_type # byte 0, accessed by msg.data[0] SHOULD ALWAYS BE 2
        self.data_type = data_type # byte 1, accessed by msg.data[1] SHOULD ALWAYS BE 4
        self.sensor_id = sensor_id # should not be necessary for the MC
        self.raw_data = raw_data # byte 2 to 8,  could be int or float (for throttle)
        # sensor id?


# process the GRPC message, CREATE THE CAN FRAME, converting grpc data to can data
def process_GRPC_message(grpc_msg):  
    # Example of mapping field1 (int) and field2 (float) into CAN format
    can_data = bytearray(8)  # research if ur using bytearray correctly

    # can_data = [command, data, 0,0,0,0,0]
    # command is usually 1 byte, other 7 are for data

    # will need to DECODE all the messages for MC

    # need to adjust this to the proper values
    struct.pack_into("<i", can_data, 0, grpc_msg.board_type)  # Pack board_type as a 1-byte int (this case it is always MC = 2)
    struct.pack_into("<i", can_data, 1, grpc_msg.data_type)  # Pack field1 as a 1-byte int
    struct.pack_into("<f", can_data, 2, grpc_msg.raw_data)  # Pack field2 as a 7-byte float
    # field2 must be a float

    # Construct a CAN message with a unique ID and packed data
    can_msg = can.Message(arbitration_id=0x123, data=can_data, is_extended_id=False)  # arbitration_id changed later, is_extended not needed as we only need 11-bit identifier
    return can_msg


# Send via CAN bus to MC, in this case with the grpc_msg
def send_CAN(grpc_msg, bus):  # the bus is declared here
    can_msg = process_GRPC_message(grpc_msg)
    try:
        bus.send(can_msg)
        print("message sent")
    except can.CanError:
        print("message failed to send")


# Test usage (in reality you'd input a real grpc message into the class)
grpc_msg = GRPCMessage(board_type=2, data_type=4) # only has two fields as of now
# Assume `bus` is a CAN bus instance configured for your network
# send_grpc_over_can(grpc_msg, bus)

def listen_for_GRPC_messages(): # do i need to do this here or could i do it in the client file?
    return 0

# test run
def main():
    # import sys
    # print(sys.path)
    grpc_client.run() # recieves the message from the server, if server is running
    return 0   # coming very soon!

main()