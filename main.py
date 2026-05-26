from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from datetime import datetime
import os

from s3 import s3, BUCKET
from db import conn, cur

app = FastAPI()
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

def is_allowed(filename: str):
    return filename.split(".")[-1].lower() in ALLOWED_EXTENSIONS

# POST: subir imagen

@app.post("/upload")
async def upload_image(
    username: str = Form(...),
    file: UploadFile = File(...)
):

    # VALIDACIÓN EXTENSIÓN
    if not is_allowed(file.filename):
        raise HTTPException(status_code=415, detail="Formato no permitido")

    # ruta en S3
    s3_key = f"users/{username}/{file.filename}"

    # subir a S3
    s3.upload_fileobj(file.file, BUCKET, s3_key)

    # guardar en RDS
    cur.execute("""
        INSERT INTO images (username, image_path)
        VALUES (%s, %s)
    """, (username, s3_key))

    conn.commit()

    return {
        "message": "Imagen subida correctamente",
        "s3_path": s3_key
    }



# GET: obtener imagen

@app.get("/image")
def get_image(username: str, image_name: str):

    s3_key = f"users/{username}/{image_name}"

    cur.execute("""
        SELECT image_path, created_at
        FROM images
        WHERE username=%s AND image_path=%s
    """, (username, s3_key))

    result = cur.fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")

    url = s3.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": BUCKET,
            "Key": s3_key
        },
        ExpiresIn=3600
    )

    return {
        "url": url,
        "uploaded_at": result[1]
    }