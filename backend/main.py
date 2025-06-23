from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import products, checkout, admin


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router, prefix="/api")
app.include_router(checkout.router, prefix="/api")
# app.include_router(categories.router, prefix="/api")
app.include_router(admin.router, prefix="/api")


# @app.get("/")
# def read_root():
#     return {"Hello": "World"}
