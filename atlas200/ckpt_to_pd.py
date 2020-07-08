#2020.7.8 by mengjun V1.0
#ckpt_to_pd tf version 1.14.0
#trian tf version 1.15.3

import tensorflow as tf
from tensorflow.python.framework import graph_util
from tensorflow.python.platform import gfile

def freeze_graph(input_path,output_path):
    output_node_names="yolov3/yolov3_head/feature_map_1,yolov3/yolov3_head/feature_map_2,yolov3/yolov3_head/feature_map_3"
    saver=tf.train.import_meta_graph(input_path+'.meta',clear_devices=True)
    graph = tf.get_default_graph()
    input_graph_def=graph.as_graph_def()
    with tf.Session() as sess:
        saver.restore(sess,input_path)
        output_graph_def=graph_util.convert_variables_to_constants(
            sess=sess,
            input_graph_def=input_graph_def,
            output_node_names=output_node_names.split(',')
        )
        with tf.gfile.GFile(output_path,'wb') as fgraph:
            fgraph.write(output_graph_def.SerializeToString())

if __name__=="__main__":
    input_path='darknet_weights/my_yolov3.ckpt'
    output_path='darknet_weights/my_yolov3_digger.pb'
    freeze_graph(input_path,output_path)
