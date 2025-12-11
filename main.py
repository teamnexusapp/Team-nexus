from fastapi import FastAPI
from routers import auth, cycles, insights, users,messages
from fastapi.middleware.cors import CORSMiddleware
import models
from database import engine




app = FastAPI()

# CORS setup
origins = [
    "http://localhost:3000",  # React dev server
    "http://127.0.0.1:3000",
    "https://teamnexuss.netlify.app/"  # production frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # List of allowed origins
    allow_credentials=True,      # Allow cookies, headers with credentials
    allow_methods=["*"],         # GET, POST, PUT, DELETE
    allow_headers=["*"],         # Allow all headers
)


models.Base.metadata.create_all(bind=engine)



app.include_router(auth.router)
app.include_router(users.router)
app.include_router(cycles.router)
app.include_router(insights.router)
app.include_router(messages.router)
