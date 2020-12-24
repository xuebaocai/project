from .ssd_classes import get_cls_dict,DIGGER_CLASSES_LIST
from .visualization import BBoxVisualization
from .publish import Publish
import cv2

class Point():
    def __init__(self):
        self.x = 0
        self.y = 0

def ray_casting(p, poly):
    if len(poly) < 3:
        return False
    flag = False
    l = len(poly)
    j = l - 1
    for i in range(0, l):
        sx = poly[i][0]
        sy = poly[i][1]
        tx = poly[j][0]
        ty = poly[j][1]
        if (sx == p.x and sy == p.y) or (tx == p.x and ty == p.y):
            return True
        if (sy < p.y <= ty) or (sy >= p.y > ty):
            x = sx + (p.y - sy) * (tx - sx) / (ty - sy)
            if x == p.x:
                return True
            if x > p.x:
                flag = not flag
        j = i
        i += 1
    return flag

def is_working(work_time):
    if int(work_time[0]) <= int(time.strftime("%H%M%S")) <= int(work_time[1]):
      return True
    else:
      return False

def DataSynchronization(result,img_list,model,alarm_type1,alarm_type2,Zone,Channel,Host,Polygon):
  pub = Publish(host=Host)
  cls_dict = get_cls_dict(model.split('_')[-1])
  vis = BBoxVisualization(cls_dict)
  for i in range(len(result)):
    boxes, confs, clss = result[i][0],result[i][1],result[i][2]
    print(boxes, confs, clss)
    img, txt = vis.draw_bboxes(img_list[0][i], boxes, confs, clss)
    alarm = str(txt).split(' ')[0]
    #print(alarm)
    if alarm in DIGGER_CLASSES_LIST:
      if alarm == 'fire':
        img_signal = threading.Thread(target=pub.send_img,
                                                      args=('/zn/aicamera/{}/{}/img'.format(Zone,Channel), img,))
        img_signal.start()

        msg_signal = threading.Thread(target=pub.send_msg,
                                                      args=('/zn/aicamera/{}/{}/alarm'.format(Zone,Channel),'alarm_type-{},time-{}'.format(alarm,time.ctime()),))
        msg_signal.start()
        
      if alarm == 'person':
        if alarm_type+str(i+1) == 'boundary_intrude':
            pt = Point()
            for bb in boxes:
                 pt.x = int((bb[0]+bb[2]) * 0.5)
                 pt.y = int(0.3 * bb[1] + 0.7 * bb[3]) 
            flag = ray_casting(pt,Polygon)
            if flag == True:
              img_signal = threading.Thread(target=pub.send_img,
                                                      args=('/zn/aicamera/{}/{}/img'.format(Zone,Channel), img,))
              img_signal.start()

              msg_signal = threading.Thread(target=pub.send_msg,
                                                      args=('/zn/aicamera/{}/{}/alarm'.format(Zone,Channel),'alarm_type-{},time-{}'.format(alarm,time.ctime()),))
              msg_signal.start()
