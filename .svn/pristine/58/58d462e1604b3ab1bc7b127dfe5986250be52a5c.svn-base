curl http://172.16.4.15:8000/api/sns/follow_launch
curl http://172.16.4.15:8000/api/sns/get_friend_list
curl http://172.16.4.15:8000/api/sns/test_chat2
# 查找用户
curl http://172.16.4.15:8000/api/sns/search_user?userId=227003&phone=0
curl http://172.16.4.15:8000/api/sns/search_user?userId=10001&phone=0
curl http://192.168.10.18:8000/api/sns/search_user?userId=10001&phone=0
# 添加好友
curl http://172.16.4.15:8000/api/sns/follow_launch?userId=10001&targetUserId=10002&hello="hi,all"&origin=1
# 处理添加好友
curl http://172.16.4.15:8000/api/sns/follow_landfall?userId=10005&targetUserId=10001&code=1
curl http://192.168.10.18:8000/api/sns/follow_landfall?userId=10002&targetUserId=10003&code=1
# 待处理好友列表
curl http://172.16.4.15:8000/api/sns/get_follow_list?userId=10000
curl http://172.16.4.15:8000/api/sns/get_follow_list?userId=10001
# 好友列表
curl http://172.16.4.15:8000/api/sns/get_friend_list?userId=10001
curl http://192.168.10.18:8000/api/sns/get_friend_list?userId=10001

# 检查好友
curl http://172.16.4.15:8000/api/sns/check_friend?userId=10000&targetUserId=10001
curl http://172.16.4.15:8000/api/sns/get_vs_record_list?userId=10000
curl http://172.16.4.15:8000/api/sns/save_vs_record?userId=10005&targetUserId=10001&code=1

# 最近匹配记录
curl http://192.168.10.18:8000/api/sns/get_vs_record_list?userId=1721054

# 删除好友
curl http://192.168.10.18:8000/api/sns/del_friend?userId=10005&targetUserId=10001

# 设置匹配信息
curl http://172.16.4.15:8000/api/sns/setting_vs_demand?userId=10005&gender=1&age=2
curl http://172.16.4.15:8000/api/sns/get_vs_demand?userId=10005