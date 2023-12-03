from typing import Union, Annotated
from contextlib import asynccontextmanager
from utils import *
from fastapi import FastAPI, File, Form, UploadFile
import torch
from PIL import Image
from io import BytesIO

global chatModel
chatModel = None


@asynccontextmanager
async def ModelLifespan(app: FastAPI):
    global chatModel
    print("Loading Model...")
    chatModel = LLavaChat(load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type='nf4',
                    device_map = 'auto',)
    print("Model Loaded...")
    yield
    chatModel = None
    
    

app = FastAPI(lifespan=ModelLifespan)


@app.get("/")
def read_root():
    return {"Hello": "World", 'test': str(chatModel)}


@app.post("/begin_conversation")
async def begin_conversation(prompt: Annotated[str, Form()], 
                        image: Annotated[UploadFile, File()],
                        ):
    content = await image.read()
    image = Image.open(BytesIO(content)).convert('RGB')
    response = chatModel.start_new_chat(image, prompt)
    #owais sucks too hard
    return {
        "prompt": prompt,
        "response" : response
    }


@app.post("/converse")
async def converse(prompt: Annotated[str, Form()],):
    response = chatModel.continue_chat(prompt)
    return {
        "prompt": prompt,
        "response": response
    }


@app.get("/get_convo_history")
async def converse():
    history = chatModel.conversation_history()
    return {
        "history": history,
    }

