import os
import pickle

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "Assets")
with open(os.path.join(ASSET_DIR, 'catboost_model.pkl'), 'rb') as f:
    catboost_model = pickle.load(f)
with open(os.path.join(ASSET_DIR, 'onehot_encoder.pkl'), 'rb') as f:
    encoder = pickle.load(f)
with open(os.path.join(ASSET_DIR, 'minmax_scaler.pkl'), 'rb') as f:
    scaler = pickle.load(f)
