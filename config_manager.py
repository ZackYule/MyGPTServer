import json


class Config:

    def __init__(self, config_file='config.json'):
        with open(config_file, 'r') as f:
            self.config = json.load(f)

    def get(self, key):
        return self.config.get(key)


# 创建一个全局配置对象
config = Config()


# 用于直接从其他文件访问配置的辅助函数
def get_config(key):
    return config.get(key)
