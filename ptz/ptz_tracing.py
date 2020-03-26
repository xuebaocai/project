#2020.3.26
#所在坐标转换成云台绝对旋转
from time import sleep
from onvif import ONVIFCamera
import zeep

XMAX = 1
XMIN = -1
YMAX = 1
YMIN = -1


def zeep_pythonvalue(self, xmlvalue):
    return xmlvalue


def perform_move(ptz, request, timeout):
    # Start continuous move
    ptz.ContinuousMove(request)
    # Wait a certain time
    sleep(timeout)
    # Stop continuous move
    ptz.Stop({'ProfileToken': request.ProfileToken})


def absolute_move(X,Y,X_threshold=320,Y_threshold = 240,find=False):
    #水平初始位置和旋转速度
    pan = 1
    pan_speed = 0.25
    #竖直初始位置和旋转速度
    tilt = 1
    tilt_speed = 0.25
    #缩放
    zoom = 1
    zoom_speed = 1
    # ip,端口，用户名，密码
    mycam = ONVIFCamera('192.168.18.251', 80, 'admin', '182333')
    # Create media service object
    media = mycam.create_media_service()
    # Create ptz service object
    ptz = mycam.create_ptz_service()

    # Get target profile
    zeep.xsd.simple.AnySimpleType.pythonvalue = zeep_pythonvalue
    media_profile = media.GetProfiles()[0]

    # Get PTZ configuration options for getting absolute move range
    request = ptz.create_type('GetConfigurationOptions')
    request.ConfigurationToken = media_profile.PTZConfiguration.token
    # ptz_configuration_options = ptz.GetConfigurationOptions(request)

    request = ptz.create_type('AbsoluteMove')
    request.ProfileToken = media_profile.token
    ptz.Stop({'ProfileToken': media_profile.token})

    if request.Position is None:
        request.Position = ptz.GetStatus({'ProfileToken': media_profile.token}).Position
    if request.Speed is None:
        request.Speed = ptz.GetStatus({'ProfileToken': media_profile.token}).Position


    #request.Position.PanTilt.x = pan
    #request.Speed.PanTilt.x = pan_speed

    #request.Position.PanTilt.y = tilt
    #request.Speed.PanTilt.y = tilt_speed

    #request.Position.Zoom = zoom
    #request.Speed.Zoom = zoom_speed

    #ptz.AbsoluteMove(request)
    #如果找到，云台追踪
    if find == True:
        if abs(X - X_threshold)>=50:
            request.Position.PanTilt.x = pan*(X/(2*X_threshold))
            request.Speed.PanTilt.x = pan_speed

        if abs(Y - Y_threshold)>=50:
            request.Position.PanTilt.y = tilt*(Y/(2*Y_threshold))
            request.Speed.PanTilt.y= tilt_speed
        ptz.AbsoluteMove(request)



if __name__ == '__main__':
    absolute_move()