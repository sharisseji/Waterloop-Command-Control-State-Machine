# sends a test message in response to a request

import grpc
from concurrent import futures
import test_pb2
import test_pb2_grpc

class TestService(test_pb2_grpc.TestServiceServicer):
    def SendTestMessage(self, request, context):
        if request.board_type == test_pb2.BoardType.MC:
            # if request.HasField("mc_data_type"):
            #     # Example response for MCDataType
            #     return test_pb2.TestResponse(
            #         example_message="MC data received",
            #         motor_status="Motor is running smoothly",
            #         motor_rpm=3200
            #     )
            #if request.board_type == test_pb2.MC:  # Only handle MC board type
            if request.HasField("mc_data_type"):
                mc_type = request.mc_data_type

                # Generate a response based on the mc_data_type
                if mc_type == test_pb2.BATTERY_VOLTAGE:
                    return test_pb2.TestResponse(
                        message="Battery voltage data",
                        battery_voltage=48.5
                    )
                elif mc_type == test_pb2.BATTERY_CURRENT:
                    return test_pb2.TestResponse(
                        message="Battery current data",
                        battery_current=120.3
                    )
                elif mc_type == test_pb2.SPEED:
                    return test_pb2.TestResponse(
                        message="Motor speed data",
                        speed=3200
                    )
                elif mc_type == test_pb2.MOTOR_TEMP:
                    return test_pb2.TestResponse(
                        message="Motor temperature data",
                        motor_temp=75.2
                    )
                elif mc_type == test_pb2.DRIVING_DIRECTION:
                    return test_pb2.TestResponse(
                        message="Driving direction data",
                        driving_direction="Forward"
                    )
                elif mc_type == test_pb2.VOLTAGE:
                    return test_pb2.TestResponse(
                        message="Motor voltage data",
                        voltage=400.1
                    )
                elif mc_type == test_pb2.CURRENT:
                    return test_pb2.TestResponse(
                        message="Motor current data",
                        current=35.7
                    )
                elif mc_type == test_pb2.CTRL_TEMP:
                    return test_pb2.TestResponse(
                        message="Controller temperature data",
                        ctrl_temp=60.5
                    )
                else:
                    return test_pb2.TestResponse(message="Unknown MC data type")
            else:
                return test_pb2.TestResponse(message="Invalid data type for MC")
        else:
            return test_pb2.TestResponse(message="Unsupported board type")
        # print(f"Received request: {request.message}")
        # return test_pb2.TestResponse(message="Test response message")  # this is when the actual message gets delivered

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    test_pb2_grpc.add_TestServiceServicer_to_server(TestService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server is running on port 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
