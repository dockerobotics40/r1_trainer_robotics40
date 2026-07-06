import rclpy
from rclpy.node import Node
import cv2
import numpy as np
from unitree_go.msg import Go2FrontVideoData


class CameraViewerNode(Node):
    def __init__(self):
        super().__init__('r1_camera_viewer')
        self.declare_parameter('resolution', '360p')
        self._res = self.get_parameter('resolution').get_parameter_value().string_value

        self.subscription = self.create_subscription(
            Go2FrontVideoData,
            '/frontvideostream',
            self._callback,
            10
        )
        self.get_logger().info(f'R1 Camera Viewer iniciado — resolución: {self._res}')

    def _callback(self, msg: Go2FrontVideoData):
        if self._res == '720p':
            raw = msg.video720p
        elif self._res == '180p':
            raw = msg.video180p
        else:
            raw = msg.video360p

        if not raw:
            return

        data = bytes(raw) if isinstance(raw, (list, bytearray)) else raw
        arr = np.frombuffer(data, dtype=np.uint8)
        frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if frame is None:
            self.get_logger().warn('No se pudo decodificar el frame', throttle_duration_sec=5.0)
            return

        cv2.imshow(f'R1 Camera ({self._res})', frame)
        if cv2.waitKey(1) == 27:  # ESC para salir
            rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    node = CameraViewerNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        cv2.destroyAllWindows()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
