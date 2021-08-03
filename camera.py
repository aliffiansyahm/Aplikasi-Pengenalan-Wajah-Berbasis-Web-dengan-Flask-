import cv2
from imutils.video import WebcamVideoStream

class VideoCamera(object):
    def __init__(self,ip):
        # self.stream = WebcamVideoStream(src=0).start()
        # self.stream = WebcamVideoStream(src='http://192.168.1.14:4747/video').start()
        self.ip = ip
        self.stream = WebcamVideoStream(src=self.ip).start()

    def __del__(self):
        self.stream.stop()

    def get_frame(self):
        image = self.stream.read()
        ret,jpeg = cv2.imencode('.jpg',image)
        data = []
        data.append(jpeg.tobytes())
        return data