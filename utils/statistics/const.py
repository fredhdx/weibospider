"""常数"""

def get_common_keys():
    keys = ['事件名',
            '微博名称',
            '微博属性',
            '认证信息',
            '粉丝拥有量',
            '微博等级',
            '网址',
            '发布时间',
            '转发数',
            '点赞数',
            '评论数',
            '第一层转发',
            '第二层转发',
            '第三层转发',
            '第四层转发',
            '四层以上转发',
            '普通用户数量',
            '个人认证占比',
            '机构认证占比',
            ]

    for i in range(1, 11):
        keys.append('昵称{}'.format(i))
        keys.append('认证类型{}'.format(i))
        keys.append('粉丝数{}'.format(i))
        keys.append('微博数{}'.format(i))
        keys.append('等级{}'.format(i))
        keys.append('认证信息{}'.format(i))
        keys.append('转发数{}'.format(i))
        keys.append('转发时间{}'.format(i))

    for i in range(1, 11):
        keys.append('c昵称{}'.format(i))
        keys.append('c认证类型{}'.format(i))
        keys.append('c粉丝数{}'.format(i))
        keys.append('c微博数{}'.format(i))
        keys.append('c等级{}'.format(i))
        keys.append('c认证信息{}'.format(i))
        keys.append('c评论时间{}'.format(i))
        # keys.append('次级评论数{}'.format(i))
        keys.append('c点赞数{}'.format(i))
    return keys
