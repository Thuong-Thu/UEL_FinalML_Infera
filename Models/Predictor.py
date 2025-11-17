
import os
import pickle
import pandas as pd
import numpy as np
from Final_HocMay.connector.connector import Connector

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSET_DIR = os.path.join(BASE_DIR, "Assets")
CACHE_DIR = os.path.join(ASSET_DIR, "cache")
os.makedirs(CACHE_DIR, exist_ok=True)


with open(os.path.join(ASSET_DIR, 'catboost_model.pkl'), 'rb') as f:
    catboost_model = pickle.load(f)

with open(os.path.join(ASSET_DIR, 'onehot_encoder.pkl'), 'rb') as f:
    encoder = pickle.load(f)
if not hasattr(encoder, 'feature_name_combiner'):
    encoder.feature_name_combiner = 'concat'

with open(os.path.join(ASSET_DIR, 'minmax_scaler.pkl'), 'rb') as f:
    scaler = pickle.load(f)

db = Connector(database="data")
db.connect()


def _load(sql: str) -> pd.DataFrame:
    return db.queryDataset(sql)


train_for_lag = _load("""
    SELECT `date`, store_nbr, family, sales 
    FROM data.cleaned_train
    ORDER BY `date`
""")
train_for_lag['date'] = pd.to_datetime(train_for_lag['date'])

holiday = _load("""
    SELECT `date`, type, locale, locale_name, description, transferred 
    FROM data.holidays_events
""")
holiday['date'] = pd.to_datetime(holiday['date'])

stores = _load("""
    SELECT store_nbr, city, state, type, cluster 
    FROM data.stores
""")
stores['store_nbr'] = stores['store_nbr'].astype(int)

FAMILIES = [
    'AUTOMOTIVE', 'BABY CARE', 'BEAUTY', 'BEVERAGES', 'BOOKS', 'BREAD/BAKERY', 'CELEBRATION',
    'CLEANING', 'DAIRY', 'DELI', 'EGGS', 'FROZEN FOODS', 'GROCERY I', 'GROCERY II', 'HARDWARE',
    'HOME AND KITCHEN I', 'HOME AND KITCHEN II', 'HOME APPLIANCES', 'HOME CARE', 'LADIESWEAR',
    'LAWN AND GARDEN', 'LINGERIE', 'LIQUOR,WINE,BEER', 'MAGAZINES', 'MEATS', 'PERSONAL CARE',
    'PET SUPPLIES', 'PLAYERS AND ELECTRONICS', 'POULTRY', 'PREPARED FOODS', 'PRODUCE',
    'SCHOOL AND OFFICE SUPPLIES', 'SEAFOOD'
]

def get_cache_file(store_nbr: int, family: str) -> str:
    safe_family = family.replace(' ', '_').replace('/', '_').replace('\\', '_')
    return os.path.join(CACHE_DIR, f"cache_{store_nbr}_{safe_family}.csv")

def load_cache(store_nbr: int, family: str) -> pd.DataFrame:
    cache_file = get_cache_file(store_nbr, family)
    if os.path.exists(cache_file):
        try:

            df = pd.read_csv(cache_file, parse_dates=['date'], date_format='%Y-%m-%d')
            if 'onpromotion' not in df.columns:
                df['onpromotion'] = 0

            df = df.drop_duplicates(subset=['date'], keep='last')
            return df
        except Exception as e:
            print(f"[CACHE] Lỗi đọc cache {cache_file}: {e}")
    mask = (train_for_lag['store_nbr'] == store_nbr) & (train_for_lag['family'] == family)
    df = train_for_lag[mask][['date', 'store_nbr', 'family', 'sales']].copy()
    df['onpromotion'] = 0
    return df

def save_cache(store_nbr: int, family: str, df: pd.DataFrame):
    df = df.drop_duplicates(subset=['date'], keep='last')
    cache_file = get_cache_file(store_nbr, family)
    try:
        df.to_csv(cache_file, index=False, date_format='%Y-%m-%d')
    except Exception as e:
        print(f"[CACHE] Lỗi lưu cache {cache_file}: {e}")

def predict_any_date(date_str: str, store_nbr: int, family: str, onpromotion: int = 0) -> float:
    try:
        target_date = pd.to_datetime(date_str)
    except Exception:
        return 0.0
    if family not in FAMILIES or not (1 <= store_nbr <= 54):
        return 0.0
    cache = load_cache(store_nbr, family)
    if cache.empty:
        return 0.0
    match = cache[(cache['date'] == target_date) & (cache['onpromotion'] == onpromotion)]
    if not match.empty:
        return round(float(match.iloc[0]['sales']), 2)
    cache = cache[cache['date'] != target_date]
    current_date = cache['date'].max() + pd.Timedelta(days=1) if not cache.empty else train_for_lag['date'].min()
    pred = 0.0

    while current_date <= target_date:

        future_df = pd.DataFrame({
            'date': [current_date],
            'store_nbr': [store_nbr],
            'family': [family],
            'onpromotion': [onpromotion]
        })
        df2 = pd.merge(future_df, holiday, on='date', how='left')
        df2 = pd.merge(df2, stores, on='store_nbr', how='left')
        df2 = df2.rename(columns={'type_x': 'holiday_type', 'type_y': 'store_type'})

        def fix_transfer(row):
            if pd.isna(row.get('holiday_type')) or row['holiday_type'] != 'Transfer':
                return row['date']
            m = holiday[
                (holiday['description'] == row['description']) &
                (holiday['type'] != 'Transfer') &
                (holiday['date'] != row['date'])
            ]
            return m.iloc[0]['date'] if not m.empty else row['date']

        df2['date'] = df2.apply(fix_transfer, axis=1)
        df2.drop_duplicates(inplace=True)
        for c in ['holiday_type', 'locale', 'locale_name', 'description', 'transferred']:
            df2[c] = df2[c].fillna('No holiday')
        df2['holiday_status'] = df2['holiday_type'].apply(
            lambda x: 'No holiday' if x in ['No holiday', 'Work Day'] else 'Holiday'
        )
        df2['year'] = df2['date'].dt.year
        df2['month'] = df2['date'].dt.month
        df2['dayofmonth'] = df2['date'].dt.day
        df2['dayofweek'] = df2['date'].dt.dayofweek
        df2['quarter'] = df2['date'].dt.quarter
        df2['is_weekend'] = df2['dayofweek'].isin([5, 6]).astype(int)
        df2['month_sin'] = np.sin(2 * np.pi * df2['month'] / 12)
        df2['month_cos'] = np.cos(2 * np.pi * df2['month'] / 12)
        df2['dayofweek_sin'] = np.sin(2 * np.pi * df2['dayofweek'] / 7)
        df2['dayofweek_cos'] = np.cos(2 * np.pi * df2['dayofweek'] / 7)
        df2['sales'] = np.nan
        full = pd.concat([cache, df2[['date', 'store_nbr', 'family', 'sales', 'onpromotion']]], ignore_index=True)
        full = full.sort_values('date')

        def add_lag(g):
            g = g.sort_values('date')
            g['sales_lag_1'] = g['sales'].shift(1)
            g['sales_lag_7'] = g['sales'].shift(7)
            g['sales_rolling_7'] = g['sales'].rolling(7, min_periods=1).mean()
            g['sales_rolling_30'] = g['sales'].rolling(30, min_periods=1).mean()
            return g

        full = full.groupby(['store_nbr', 'family'], group_keys=False).apply(add_lag)
        row_match = full[full['date'] == current_date]
        if row_match.empty:
            current_date += pd.Timedelta(days=1)
            continue
        row = row_match.iloc[0]
        X_temp = df2.copy()
        hist_mean = cache['sales'].mean() if not cache.empty else 0
        for c in ['sales_lag_1', 'sales_lag_7', 'sales_rolling_7', 'sales_rolling_30']:
            val = row.get(c, hist_mean)
            X_temp[c] = hist_mean if pd.isna(val) else val

        keep = [
            'store_nbr', 'family', 'onpromotion', 'holiday_status', 'month', 'dayofmonth',
            'dayofweek', 'year', 'quarter', 'is_weekend',
            'sales_lag_1', 'sales_lag_7', 'sales_rolling_7', 'sales_rolling_30',
            'month_sin', 'month_cos', 'dayofweek_sin', 'dayofweek_cos'
        ]
        X_temp = X_temp[keep]
        cat_cols = ['family', 'holiday_status']
        num_cols = [c for c in keep if c not in cat_cols and c in scaler.feature_names_in_]

        try:
            cat_enc = pd.DataFrame(encoder.transform(X_temp[cat_cols]),
                                   columns=encoder.get_feature_names_out(),
                                   index=X_temp.index)
            num_scl = pd.DataFrame(scaler.transform(X_temp[num_cols]),
                                   columns=num_cols,
                                   index=X_temp.index)
            X = pd.concat([cat_enc, num_scl], axis=1)
            pred_log = catboost_model.predict(X)[0]
            pred = max(np.expm1(pred_log), 0)
        except Exception as e:
            print(f"[PREDICT ERROR] {e}")
            pred = hist_mean

        # Cập nhật cache
        new_row = pd.DataFrame({
            'date': [current_date],
            'store_nbr': [store_nbr],
            'family': [family],
            'sales': [pred],
            'onpromotion': [onpromotion]
        })
        cache = pd.concat([cache, new_row], ignore_index=True)

        if current_date == target_date:
            save_cache(store_nbr, family, cache)
            return round(float(pred), 2)
        current_date += pd.Timedelta(days=1)
    save_cache(store_nbr, family, cache)
    return round(float(pred), 2)

def predict_for_store_date(date_str: str, store_nbr: int) -> pd.DataFrame:
    predictions = []
    target_date = pd.to_datetime(date_str)

    for family in FAMILIES:
        cache = load_cache(store_nbr, family)
        match = cache[cache['date'] == target_date]
        if not match.empty:
            onpromo = int(match.iloc[0]['onpromotion'])
        else:
            onpromo = 0
        pred = predict_any_date(date_str, store_nbr, family, onpromotion=onpromo)
        predictions.append((family, pred, onpromo))
    df = pd.DataFrame(predictions, columns=['FAMILY', 'SALES', 'USED_PROMO'])
    return df.sort_values(by='SALES', ascending=False).reset_index(drop=True)