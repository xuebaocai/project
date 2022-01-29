import pandas as pd
from sqlalchemy import create_engine

#项目对应id
project_tuple = ('0pyMwScXYd1ybaiL1VWoGBP','0is9aJL9J9b58wCdteCavxk','0m9arjvIRR2tGD3yjvuRsbyt')

#数据库连接
engine = create_engine('oracle+cx_oracle://zedx_db:f#2#!dx_db@2@192.168.100.182:1521/ORCLCDB')

#请求 TDM_C_WELD_JOINT表
TDM_C_WELD_JOINT_df = pd.read_sql_query('select * from PRO_PNPM_PLM.TDM_C_WELD_JOINT', engine)
#print(TDM_C_WELD_JOINT_df.describe) 01/29 213839 x 55

#请求 TDM_C_PIPE_GROOVE_GROUP表
TDM_C_PIPE_GROOVE_GROUP_df = pd.read_sql_query('select * from PRO_PNPM_PLM.TDM_C_PIPE_GROOVE_GROUP', engine)
#print(TDM_C_PIPE_GROOVE_GROUP_df.describe) # 01/29 194017 x 43

#请求 TDM_C_WELD表
TDM_C_WELD_df = pd.read_sql_query('select * from PRO_PNPM_PLM.TDM_C_WELD', engine)
#print(TDM_C_WELD_df.describe) # 01/29 192035 x 53

#请求 TDM_C_PIPE_LINE_TEST
TDM_C_PIPE_LINE_TEST_df = pd.read_sql_query('select * from PRO_PNPM_PLM.TDM_C_PIPE_LINE_TEST', engine)
#print(TDM_C_PIPE_LINE_TEST_df.describe) # 01/29 304188 x 45

#请求 TDM_C_TEST_DEFECTION
TDM_C_TEST_DEFECTION_df = pd.read_sql_query('select * from PRO_PNPM_PLM.TDM_C_TEST_DEFECTION', engine)
#print(TDM_C_TEST_DEFECTION_df.describe) # 01/29 321697 x 33



########

#滤除TDM_C_WELD_JOINT表其他项目
TDM_C_WELD_JOINT_df = TDM_C_WELD_JOINT_df[TDM_C_WELD_JOINT_df['project_id'].apply(lambda x:x in project_tuple)]
#print(TDM_C_WELD_JOINT_df.describe) 01/29 89094 x 55

#保留ID.PROJECT_ID，WELDING_PROCEDURE_ID，WELD_NUMBER，WORK_TEAM_ID
TDM_C_WELD_JOINT_df_retain_col = ['id','project_id','welding_procedure_id','weld_number','work_team_id']
TDM_C_WELD_JOINT_df = TDM_C_WELD_JOINT_df.drop([col for col in TDM_C_WELD_JOINT_df.columns \
                                                 if col not in TDM_C_WELD_JOINT_df_retain_col],\
                                                 axis=1)
#print(TDM_C_WELD_JOINT_df.describe) 01/29  89094 x 5

#TDM_C_WELD_JOINT_df id-->weld_joint_id
TDM_C_WELD_JOINT_df.rename(columns={'id':'weld_joint_id'},inplace=True)



#滤除TDM_C_PIPE_GROOVE_GROUP_df表其他项目
TDM_C_PIPE_GROOVE_GROUP_df = TDM_C_PIPE_GROOVE_GROUP_df[TDM_C_PIPE_GROOVE_GROUP_df['project_id'].apply(lambda x:x in project_tuple)]
#print(TDM_C_PIPE_GROOVE_GROUP_df.describe 82775  x 43

TDM_C_PIPE_GROOVE_GROUP_df_retain_col = ['weld_joint_id','groove_type','OUTSIDE_GROOVE_Α','OUTSIDE_GROOVE_Β',
                                         'INNER_GROOVE_Γ','blunt_edge_p','blunt_change_point_h','inner_groove_height_h',
                                         'tube_cleaning','wrong_side','counterpart_clearance_b','max_wrong_side',
                                         'inner_diameter_deviation','preheat_time','preheat_the_width',
                                         'bevel_machine_number','group_on_device_number','preheat_device_number']

TDM_C_PIPE_GROOVE_GROUP_df = TDM_C_PIPE_GROOVE_GROUP_df.drop([col for col in TDM_C_PIPE_GROOVE_GROUP_df.columns \
                                                 if col not in TDM_C_PIPE_GROOVE_GROUP_df_retain_col],\
                                                 axis=1)
#print(TDM_C_PIPE_GROOVE_GROUP_df.describe) 01/29 82775  x 19

#TDM_C_PIPE_GROOVE_GROUP_df,TDM_C_WELD_JOINT_df 联立weld_joint_id
PIPE_GROOVE_GROUP_WELD_JOINT_df = pd.merge(TDM_C_WELD_JOINT_df,TDM_C_PIPE_GROOVE_GROUP_df,on='weld_joint_id',how='left')



#去除重复值
PIPE_GROOVE_GROUP_WELD_JOINT_df.drop_duplicates(inplace=True)
#print(PIPE_GROOVE_GROUP_WELD_JOINT_df.describe)#89094 rows x 22


#PIPE_GROOVE_GROUP_WELD_JOINT_df = PIPE_GROOVE_GROUP_WELD_JOINT_df.set_index('weld_number')

########

#滤除TDM_C_WELD_df表其他项目
TDM_C_WELD_df = TDM_C_WELD_df[TDM_C_WELD_df['project_id'].apply(lambda x:x in project_tuple)]
#print(TDM_C_WELD_df.describe) 01/29 82737 x 53

TDM_C_WELD_df_retain_col = ['weld_joint_id','relative_mileage','weld_preheating_method',
                            'preheat_temperature','axial_deviation_angle']
TDM_C_WELD_df = TDM_C_WELD_df.drop([col for col in TDM_C_WELD_df.columns \
                                                 if col not in TDM_C_WELD_df_retain_col],\
                                                 axis=1)
#print(TDM_C_WELD_df.describe) 01/29 82737 x 5

#上述三表合并
GROOVE_WELD_JOINT_df = pd.merge(PIPE_GROOVE_GROUP_WELD_JOINT_df,TDM_C_WELD_df,on='weld_joint_id',how='left')
GROOVE_WELD_JOINT_df.drop_duplicates(inplace=True)
#print(GROOVE_WELD_JOINT_df.describe) #89094x 32



#滤除TDM_C_PIPE_LINE_TEST_df表其他项目
TDM_C_PIPE_LINE_TEST_df = TDM_C_PIPE_LINE_TEST_df[TDM_C_PIPE_LINE_TEST_df['project_id'].apply(lambda x:x in project_tuple)]
#print(TDM_C_PIPE_LINE_TEST_df.describe)  #146015 x 45
#保留 detection_type='AUT'
TDM_C_PIPE_LINE_TEST_df = TDM_C_PIPE_LINE_TEST_df[TDM_C_PIPE_LINE_TEST_df['detection_type']=='AUT']
#print(TDM_C_PIPE_LINE_TEST_df.describe) #78376  x 45


#id——》检测表的test_id
TDM_C_PIPE_LINE_TEST_retain_col = ['id','weld_joint_id','grade_of_evaluation','evaluation_result']
TDM_C_PIPE_LINE_TEST_df = TDM_C_PIPE_LINE_TEST_df.drop([col for col in TDM_C_PIPE_LINE_TEST_df.columns \
                                                 if col not in TDM_C_PIPE_LINE_TEST_retain_col],\
                                                 axis=1)
TDM_C_PIPE_LINE_TEST_df.rename(columns={'id':'test_id'},inplace=True)
#print(TDM_C_PIPE_LINE_TEST_df.describe) #78376 x 4
TDM_C_TEST_DEFECTION_df_retain_col = ['test_id','defection_location',
                                      'defection_property','defection_length']
TDM_C_TEST_DEFECTION_df = TDM_C_TEST_DEFECTION_df.drop([col for col in TDM_C_TEST_DEFECTION_df.columns \
                                                 if col not in TDM_C_TEST_DEFECTION_df_retain_col],
                                                 axis=1)
#print(TDM_C_TEST_DEFECTION_df.describe) 321697  x 4

#TDM_C_PIPE_LINE_TEST_df,TDM_C_TEST_DEFECTION_df合并
TEST_DEFECTION_df = pd.merge(TDM_C_PIPE_LINE_TEST_df,TDM_C_TEST_DEFECTION_df,on='test_id',how='left')

TEST_DEFECTION_df.drop_duplicates('test_id',inplace=True)

#print('5',TEST_DEFECTION_df.describe) #78376 rows x 7

GROOVE_WELD_JOINT_TEST_DEFECTION_df = pd.merge(GROOVE_WELD_JOINT_df,TEST_DEFECTION_df,on='weld_joint_id',how='left')

GROOVE_WELD_JOINT_TEST_DEFECTION_df.drop_duplicates('weld_joint_id',inplace=True)
print(GROOVE_WELD_JOINT_TEST_DEFECTION_df.describe) #89094 rows x 32



