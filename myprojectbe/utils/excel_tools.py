import pandas as pd

# ================================
# NORMALISASI NAMA KOLOM
# ================================
def normalize_columns(df):
    df.columns = [c.lower().strip() for c in df.columns]
    return df

# ================================
# 1. FILTER DINAMIS MULTI-KOLOM
# ================================
def filter_multi(df, filter_dict):
    df = normalize_columns(df)
    df_filtered = df.copy()

    for kolom, nilai_list in filter_dict.items():
        kolom = kolom.lower().strip()

        if kolom not in df_filtered.columns:
            raise Exception(f"Kolom '{kolom}' tidak ditemukan di file.")

        df_filtered = df_filtered[df_filtered[kolom].astype(str).isin(nilai_list)]

    return df_filtered

# ================================
# 2. DETEKSI DUPLIKAT
# ================================
def detect_duplicates(df, kolom_list=None):
    df = normalize_columns(df)

    if kolom_list is None:
        kolom_list = list(df.columns)
    else:
        kolom_list = [c.lower().strip() for c in kolom_list]

    df_dupe = df[df.duplicated(subset=kolom_list, keep=False)].copy()

    return df_dupe, kolom_list or list(df.columns)

# ================================
# 3. HAPUS DUPLIKAT
# ================================
def remove_duplicates(df, kolom_list=None):
    df = normalize_columns(df)

    if kolom_list is None:
        kolom_list = list(df.columns)

    df_clean = df.drop_duplicates(subset=kolom_list, keep="first")
    return df_clean

# ================================
# 4. MATCHING DATA DINAMIS
# ================================
def find_common_columns(df1, df2):
    df1_cols = [c.lower().strip() for c in df1.columns]
    df2_cols = [c.lower().strip() for c in df2.columns]
    return list(set(df1_cols) & set(df2_cols))

def match_data(df_uploaded, df_db):
    df_uploaded = normalize_columns(df_uploaded)
    df_db = normalize_columns(df_db)

    common_cols = find_common_columns(df_uploaded, df_db)

    if not common_cols:
        raise Exception("Tidak ada kolom yang cocok untuk matching.")

    merged = pd.merge(df_uploaded, df_db, on=common_cols, how="inner")

    return merged, common_cols