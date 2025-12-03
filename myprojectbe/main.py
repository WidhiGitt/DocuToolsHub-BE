from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import io
import os

from utils.excel_tools import (
    filter_multi,
    detect_duplicates,
    remove_duplicates,
    match_data
)

from auth import router as auth_router


app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register auth routes
app.include_router(auth_router)

# Root endpoint
@app.get("/")
def root():
    return {"message": "Backend is running"}


@app.post("/process")
async def process_file(
    file: UploadFile = File(...),

    filter_opt: bool = Form(False),
    filter_column: str = Form(""),
    filter_values: str = Form(""),

    detect_dupe_opt: bool = Form(False),
    remove_dupe_opt: bool = Form(False),

    matching_opt: bool = Form(False),
):
    
    content = await file.read()
    df = pd.read_excel(io.BytesIO(content))

    common_cols = None

    # 1. FILTER
    if filter_opt and filter_column and filter_values:
        filter_dict = {
            filter_column: [v.strip() for v in filter_values.split(",")]
        }

        try:
            df = filter_multi(df, filter_dict)
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=400)

    # 2. DETECT DUPLICATE
    if detect_dupe_opt:
        dupe_df, used_cols = detect_duplicates(df)

        return JSONResponse({
            "message": "Duplikat ditemukan",
            "columns_used": used_cols,
            "duplicates": dupe_df.to_dict(orient="records")
        })

    # 3. REMOVE DUPLICATE
    if remove_dupe_opt:
        df = remove_duplicates(df)

    # 4. MATCHING
    if matching_opt:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        DB_PATH = os.path.join(BASE_DIR, "db", "db.xlsx")

        try:
            db_df = pd.read_excel(DB_PATH)
        except Exception as e:
            return JSONResponse({"error": f"DB gagal dibaca: {str(e)}"}, status_code=400)

        try:
            df, common_cols = match_data(df, db_df)
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=400)

    # OUTPUT
    df = df.fillna("")

    return JSONResponse({
        "message": "Success",
        "data": df.to_dict(orient="records"),
        **({"matched_on": common_cols} if matching_opt else {})
    })