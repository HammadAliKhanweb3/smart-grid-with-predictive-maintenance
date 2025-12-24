from fastapi import FastAPI



app = FastAPI()



dataArray = []
@app.get("/user/1")
async def getUser():
    dataArray.append({"id": 1, "name": "Saad"})
    return dataArray