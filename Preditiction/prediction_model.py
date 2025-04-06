# model.py
"""模型训练模块，整合分段ARIMA参数学习和LSTM模型训练"""
from time_series_prediction.Paragraphs_ARIMA import find_segmented_arima_order, load_data_from_db
from time_series_prediction.LSTM import main as train_lstm
import pickle

def train_arima_params():
    """训练并保存分段ARIMA最佳参数"""
    sequences = load_data_from_db("time_series.db", "hotness_records")#路径问题
    best_order = find_segmented_arima_order(sequences)
    with open('best_arima_order.pkl', 'wb') as f:
        pickle.dump(best_order, f)
    print(f"分段ARIMA最佳参数已保存: {best_order}")

def train_lstm_model():
    """训练并保存LSTM模型"""
    train_lstm()

if __name__ == "__main__":
    train_arima_params()
    train_lstm_model()