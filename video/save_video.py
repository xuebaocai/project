# 2020/5/20
import cv2
import time
import avi_to_h264


def main(ip='10.164.18.1',save_time=1):
    '''
    :param ip: aicamera ip address
    :return: h264 video
    '''
    file_time = time.ctime()
    file_time = file_time.replace(' ', '_')
    rtsp_url = 'rtsp://admin:182333@{}:554'.format(ip)

    cap = cv2.VideoCapture(rtsp_url)

    codec = cv2.VideoWriter_fourcc(*'MJPG')

    fps = 25.0

    frameSize = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

    output = cv2.VideoWriter('{}.avi'.format(file_time), codec, fps, frameSize)

    ctime = 0
    ptime = time.time()
    
    while (cap.isOpened()):

        ret, frame = cap.read()

        start_t = cv2.getTickCount()

        output.write(frame)

        # stop 
        ntime = time.time()
        ctime = ntime - ptime
        if ctime >= (save_time*2.9)*60:
            break

    cap.release()
    output.release()
    cv2.destroyAllWindows()

    to_h264 = avi_to_h264.avi_to_H264(from_path='{}.avi'.format(file_time), to_path='{}.264'.format(file_time))
    to_h264.convert_byfile()

if __name__ == "__main__":
    main()
