# sends a request to the server to receive a message

import grpc
import test_pb2
import test_pb2_grpc

# function to ensure the server and client are running, for testing purposes only
def test(): 
    with grpc.insecure_channel('localhost:50051') as channel:           # change channel to ip address when testing
        stub = test_pb2_grpc.TestServiceStub(channel)
        request = test_pb2.TestRequest(message="Test request message")  # asks the server for any test message
        response = stub.SendTestMessage(request) 
        print(f"Received response: {response.message}")

# retrieves appropriate MC data from the server
def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = test_pb2_grpc.TestServiceStub(channel)

        # Example request for BATTERY_VOLTAGE
        request = test_pb2.TestRequest(
            board_type=test_pb2.MC,
            mc_data_type=test_pb2.BATTERY_VOLTAGE,
            sensor_id="sensor123",
            data=b"raw_binary_data"
        )
        response = stub.SendTestMessage(request)
        print(f"Message: {response.message}")
        print(f"Battery Voltage: {response.battery_voltage}")
        print(f"Battery Current: {response.battery_current}")
        print(f"Speed: {response.speed}")

if __name__ == '__main__':
    run()
