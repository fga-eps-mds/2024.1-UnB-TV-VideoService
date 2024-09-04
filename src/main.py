from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db  # Adicione a função de inicialização do banco de dados




from controller import commentController, scheduleController, savedVideosController, recordController, recommendationController
from controller.savedVideosController import WatchLater


# Desativado os os comentarios nos videos
# from database import SessionLocal, engine
# from model import commentModel

# commentModel.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
) 

# Inicializar o banco de dados
init_db()


app.include_router(WatchLater, prefix="/api")
#app.include_router(prefix="/api", router=commentController.comment)
app.include_router(prefix="/api", router=scheduleController.schedule)
app.include_router(prefix="/api", router=savedVideosController.favorite)
app.include_router(prefix="/api", router=recordController.Record)
app.include_router(prefix="/api", router=recommendationController.Recommendation)

@app.get("/")
async def root():
    return {"message": "Hello from Video Service"}

# if __name__ == '__main__': # pragma: no cover
#   port = 8001
#   if (len(sys.argv) == 2):
#     port = sys.argv[1]

#   uvicorn.run('main:app', reload=True, port=int(port), host="0.0.0.0")