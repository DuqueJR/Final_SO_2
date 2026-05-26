from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from datetime import datetime
import os

from s3 import s3, BUCKET

from botocore.exceptions import ClientError

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


    return {
        "message": "Imagen subida correctamente",
        "s3_path": s3_key
    }



# GET: obtener imagen

@app.get("/image")
def get_image(username: str, image_name: str):

    s3_key = f"users/{username}/{image_name}"

    

    # if not result:
    #     raise HTTPException(status_code=404, detail="Imagen no encontrada")

    # url = s3.generate_presigned_url(
    #     "get_object",
    #     Params={
    #         "Bucket": BUCKET,
    #         "Key": s3_key
    #     },
    #     ExpiresIn=3600
    # )

    try:
        response=s3.head_object(Bucket=BUCKET, Key=s3_key)

        url = s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": BUCKET,
                "Key": s3_key
         },
            ExpiresIn=3600
        )

    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
           raise HTTPException(status_code=404, detail="Imagen no encontrada")

        else:
            raise HTTPException(status_code=404, detail="Imagen no encontrada")


    return {
        "url": url,
        "uploaded_at": response["LastModified"]


    }