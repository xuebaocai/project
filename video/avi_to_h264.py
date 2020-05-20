# coding: utf-8
import sys, os

 
class avi_to_H264():
    def __init__(self,from_path,to_path):
        self.from_path = from_path
        self.to_path = to_path
 
    
    def convert_avi(self, input_file, output_file, ffmpeg_exec="ffmpeg"):
        ffmpeg = '{ffmpeg} -y -i "{infile}" -c:v libx264 -strict -2 "{outfile}"'.format(ffmpeg=ffmpeg_exec,infile=input_file, outfile=output_file)                                                                            
        f = os.popen(ffmpeg)
        ffmpegresult = f.readline()
        return ffmpegresult
 
 
    def convert_avi_to_mp4(self, input_file, output_file, ffmpeg_exec="ffmpeg"):
        return self.convert_avi(input_file, output_file, ffmpeg_exec="ffmpeg")
 
 
    def convert_byfile(self):
        if not os.path.exists(self.from_path):
            print("Sorry, you must create the directory for the output files first")
        if not os.path.exists(os.path.dirname(self.to_path)):
            os.makedirs(os.path.dirname(self.to_path), exist_ok=True)
        directory, file_name = os.path.split(self.from_path)
        raw_name, extension = os.path.splitext(file_name)
        print("Converting ", self.from_path)
        self.convert_avi_to_mp4(self.from_path, self.to_path)
 
a = mp4_to_H264(from_path = '/home/mengjun/video/zhannei.avi',to_path = '/home/mengjun/video/test.264')


a.convert_byfile()
