from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from postergen import generate_poster
from firebase_upload import upload_to_firebase
import uuid

app = FastAPI()

# Allow requests from Shopify or localhost during testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict to your Shopify domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generate-poster")
async def generate_poster_api(
    prompt: str = Form(...),
    ai_reimagine: bool = Form(False),
    customer_id: str = Form(None),
    image: UploadFile = None
):
    try:
        # Generate the poster
        original_path, watermarked_path = await generate_poster(prompt, image, ai_reimagine)

        # Upload to Firebase Storage
        original_url = upload_to_firebase(original_path)
        watermarked_url = upload_to_firebase(watermarked_path)

        return {
            "success": True,
            "prompt": prompt,
            "original_url": original_url,
            "watermarked_url": watermarked_url,
            "customer_id": customer_id or "guest_" + str(uuid.uuid4())[:8]
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
