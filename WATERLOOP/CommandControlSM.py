#########################################################################
#                           WATERLOOP                                   #
#   G7 Raspberry Pi Host Application: Command Control State Machine     #
#   Author: Sharisse Ji                                                 #
#                                                                       #
#   Description:                                                        #
#   1.  Processes an incoming gRPC message from the dashboard           # 
#       containing only motor controller commands                       #
#   2.  Packs the gRPC message data into a CAN frame                    #
#   3.  Sends the CAN message to the motor controller via can.bus       #
#########################################################################

import can  
import grpc
import test_pb2
import grpc_client  
import struct
import logging
import time

## SET UP ##
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialization of gRPC channel and stub
channel = grpc.insecure_channel('') # during testing, use computer IP address instead of localhost:50051

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


## GPRC MESSAGE DEFINITION ##
class GRPCMessage:
    """
    Defines a gRPC message object as defined the proto3 file. 
    Note that though the Command Control only sends messages to the MC, the board types 
    and sensor id must still be defined according to all gRPC message formats coming into the RPi.

    Args:
        board_type  (int): MC, Sensor, BMS
        data_type   (int): see MC_DATA_TYPES
        sensor_id   (int): ?
        raw_data  (float): in this case will contain MC data (e.g. throttle %)

    Returns:
    A gRPC message object.
    """
    def __init__(self, board_type, data_type, sensor_id, raw_data):  
        self.board_type = board_type    # byte 0, accessed by msg.data[0] should always = 2 for the MC
        self.data_type = data_type      # byte 1, accessed by msg.data[1] 
        self.sensor_id = sensor_id      # created as {board_type}+{data_type} ?
        self.raw_data = raw_data        # byte 2 to 8,  could be int or float (for throttle)


## GPRC -> CAN FUNCTIONS ##
def process_GRPC_message(grpc_msg):
    """
    Takes the data from the INCOMING gRPC message and packs it into the CAN frame

    Args: 
        grpc_msg (GPRCMessage) : contains a gRPC message object sent by the server
    """
    # Declare an 8-byte array to contain the CAN data
    can_data = bytearray(8) 

    # Pack the appropriate GRPC field data into can_data
    struct.pack_into("<i", can_data, 0, grpc_msg.board_type)    # Pack board_type as a 1-byte int (this case it is always MC = 2)
    struct.pack_into("<i", can_data, 1, grpc_msg.data_type)     # Pack field1 as a 1-byte int
    struct.pack_into("<f", can_data, 2, grpc_msg.raw_data)      # Pack field2 as a 7-byte float

    # Construct a CAN message with a unique arbitration ID and packed data from the bytearray
    can_msg = can.Message(arbitration_id=0x123, data=can_data, is_extended_id=False)  # arbitration_id will be developed later, is_extended not needed as we only need an 11-bit identifier
    return can_msg


def send_CAN(grpc_msg, bus):  
    """
    calls process_GRPC_message before sending it over the CAN bus

    Args: 
        grpc_msg (GPRCMessage) : contains the gRPC message object previously defined
        bus (bus) : contains an external declaration of a CAN bus instance from CAN.bus (will be included in the compiled RPi code)
    """
    can_msg = process_GRPC_message(grpc_msg)
    try:
        bus.send(can_msg)
        print(f"message sent on{bus.channel_info}")
    except can.CanError:
        print("message failed to send")


## IN PROGRESS ##
def listen_for_GRPC_messages(): 
    return 0


## EXAMPLE USAGE ##
# 1. Create an object of class GRPCMessage
grpc_msg = GRPCMessage(2, 4) # set board_type = 2, and data_type = 4, include the sensor id and raw_data

# 2. Process the message and send it over the CAN bus (assume 'bus' is a configured instance in this network)
# send_CAN(grpc_msg, bus) # bus has not been configured yet


## TEST ##
def main():
    # later run major checks here
    grpc_client.run() # recieves the message from the server, if server is running
    return 0   

main()