""" This module provides a configuration for this stock analysis project"""


class Config:
    """This class sets hyper parameters for this project"""

    def __init__(self):
        
        # 股票数据存储路径
        self.stock_datapath = (
            "dataset/stock.parquet.gz"
        )
        # 港股数据存储路径
        self.hsi_datapath = (
            "dataset/hsi_stock_data"
        )

        # 训练数据的起止日期
        # self.train_start_date = "2024-02-05"
        # self.train_end_date = "2024-07-05"
        self.train_start_date = "2023-01-01"
        self.train_end_date = "2025-01-31"

        # 取过去pre_days的数据特征
        self.pre_days = 10
        # 取未来post_days的数据特征
        self.post_days = 4

        # 模拟
        self.simulate_start_date = "2024-09-28"
        self.simulate_end_date = "2024-12-27"

        # 构造特征列
        self.feature_cols = []
        for i in range(self.pre_days + 1):
            self.feature_cols += [
                f"Volume_p{i}",
                f"OpenMinMax_p{i}",
                f"CloseMinMax_p{i}",
                f"maxIncreaseRatio_p{i}",
                f"increaseRatio_p{i}",
            ]

        for i in range(self.pre_days, 0, -1):
            self.feature_cols.append(f"increase_p{i}p{i-1}")

        # config
        self.log_level = "INFO"

        # configure model
        # self.transformer_config()
        
        # configure lightgbm
        # self.lightgbm_config()

    def kmeans_config(self):
        self.k = 4000

    def lightgbm_config(self):
        # # select 
        self.train_start_date = "2023-01-01"
        self.train_end_date = "2025-01-31"
        self.test_start_date = "2025-02-01"
        self.test_end_date = "2025-03-01"
        # # 模拟
        # self.simulate_start_date = "2024-12-01"
        # self.simulate_end_date = "2024-12-31"
        self.simulate_start_date = "2025-01-01"
        self.simulate_end_date = "2025-02-11"
        # 模型相关配置
        self.model_num_leaves = 64
        self.model_objective = "binary"
        self.model_metric = ["auc", "binary_logloss"]
        self.model_name = (
            f"model2_pre{self.pre_days}_post{self.post_days}"
            + f"_{self.train_start_date}_{self.train_end_date}"
        )
        self.model_path = (
            "/Users/ytqiang/workspace/StockAnalysis/checkpoints/" + self.model_name+".txt"
        )
        self.model_rounds = 50
    
    def transformer_config(self):
        # # select 
        self.train_start_date = "2024-07-01"
        self.train_end_date = "2024-12-31"
        # # 模拟
        # self.simulate_start_date = "2024-12-01"
        # self.simulate_end_date = "2024-12-31"
        self.simulate_start_date = "2025-01-01"
        self.simulate_end_date = "2025-02-11"
        self.model_name = (
            f"pre{self.pre_days}_post{self.post_days}"
            + f"_{self.train_start_date}_{self.train_end_date}"
        )
        self.model_path = (
            "/Users/ytqiang/workspace/StockAnalysis/checkpoints/convmlp/" + self.model_name
        )


    def print_config(self):
        print("********************数据相关配置********************")
        print("股票数据存储路径: ", self.stock_datapath)
        print("训练数据的起止日期: ", self.train_start_date, self.train_end_date)
        print("模拟数据的起止日期: ", self.simulate_start_date, self.simulate_end_date)
        print(f"特征列({len(self.feature_cols)}):")
        for i, col in enumerate(self.feature_cols):
            print(f"{i}: {col}\t\t", end="")
            if (i+1) % 5 == 0:
                print()
        print()
        print("********************模型相关配置********************")
        print("模型路径: ", self.model_path)
        print("模型参数: ")
        print(f"num_leaves={self.model_num_leaves}")
        print(f"objective ={self.model_objective}")
        print(f"metric={self.model_metric}")
        print(f"rounds={self.model_rounds}")

config = Config()
