#2020.3.26
#ptz absoluteMove
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


def absolute_move():
    pan = 0.5
    pan_speed = 0.25
    tilt = 0
    tilt_speed = 1
    zoom = 1
    zoom_speed = 1

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

    request.Position.PanTilt.x = pan
    request.Speed.PanTilt.x = pan_speed

    request.Position.PanTilt.y = tilt
    request.Speed.PanTilt.y = tilt_speed

    request.Position.Zoom = zoom
    request.Speed.Zoom = zoom_speed

    ptz.AbsoluteMove(request)
    print('finish')


if __name__ == '__main__':
    absolute_move()