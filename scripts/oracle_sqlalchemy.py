import pandas as pd
from sqlalchemy import create_engine

#项目对应id
project_tuple = ('0pyMwScXYd1ybaiL1VWoGBP','0is9aJL9J9b58wCdteCavxk','0m9arjvIRR2tGD3yjvuRsbyt')

#数据库连接
engine = create_engine('oracle+cx_oracle://user:password@192.168.100.182:1521/ORCLCDB')

#请求 TDM_C_WELD_JOINT表
TDM_C_WELD_JOINT_df = pd.read_sql_query('select * from PRO_PNPM_PLM.TDM_C_WELD_JOINT', engine)
#print(TDM_C_WELD_JOINT_df.describe) 01/29 213839 x 55

#请求 TDM_C_PIPE_GROOVE_GROUP表
TDM_C_PIPE_GROOVE_GROUP_df = pd.read_sql_query('select * from PRO_PNPM_PLM.TDM_C_PIPE_GROOVE_GROUP', engine)
#print(TDM_C_PIPE_GROOVE_GROUP_df.describe) # 01/29 194017 x 43

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

TDM_C_PIPE_GROOVE_GROUP_df_retain_col = ['weld_joint_id','project_id','groove_type','OUTSIDE_GROOVE_Α','OUTSIDE_GROOVE_Β',
                                         'INNER_GROOVE_Γ','blunt_edge_p','blunt_change_point_h','inner_groove_height_h',
                                         'tube_cleaning','wrong_side','counterpart_clearance_b','max_wrong_side',
                                         'inner_diameter_deviation','preheat_time','preheat_the_width']

TDM_C_PIPE_GROOVE_GROUP_df = TDM_C_PIPE_GROOVE_GROUP_df.drop([col for col in TDM_C_PIPE_GROOVE_GROUP_df.columns \
                                                 if col not in TDM_C_PIPE_GROOVE_GROUP_df_retain_col],\
                                                 axis=1)
#print(TDM_C_PIPE_GROOVE_GROUP_df.describe) 82775  x 16

#TDM_C_PIPE_GROOVE_GROUP_df,TDM_C_WELD_JOINT_df 联立weld_joint_id
PIPE_GROOVE_GROUP_WELD_JOINT_df = pd.merge(TDM_C_WELD_JOINT_df,TDM_C_PIPE_GROOVE_GROUP_df,on='weld_joint_id',how='left')
print(PIPE_GROOVE_GROUP_WELD_JOINT_df.head(2))
print(PIPE_GROOVE_GROUP_WELD_JOINT_df.describe)#89095 x 20


