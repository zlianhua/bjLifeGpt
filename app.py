from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from supabase import create_client, Client
from fastapi.middleware.cors import CORSMiddleware

SUPABASE_URL = 'https://aauhpkygxsnooxvpqqqy.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFhdWhwa3lneHNub294dnBxcXF5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE2ODc3NTc2MjQsImV4cCI6MjAwMzMzMzYyNH0.kEOf2y2gKWHwHDz2pb3fe11AI8WKosaW5MCwnLhSkwI'
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

# app.add_middleware(
#   CORSMiddleware,
#   allow_origins=["https://chat.openai.com","https://bj-life-gpt.vercel.app"],
#   allow_methods=["*"],
#   allow_headers=["*"],
#   allow_credentials=True
# )

class QueryModel(BaseModel):
    table: str
    select: str
    conditions: dict
    
class InsertModel(BaseModel):
    table: str
    data: dict

@app.post("/insert")
async def insert(data: InsertModel):
    response = supabase.table(data.table).insert(data.data).execute()

    # if response.error:
    #     raise HTTPException(status_code=400, detail=str(response.error))
    return {"message": "Insert successful", "data": response.data}    

@app.post("/query")
async def query(data: QueryModel):
    query = supabase.table(data.table).select(data.select)

    # 这里简化条件处理，具体实现依据conditions内容而定
    for condition, value in data.conditions.items():
        query = query.filter(condition, value)

    response = query.execute()

    # if response.error:
    #     raise HTTPException(status_code=400, detail=str(response.error))
    return response.data

@app.get('/openapi.json')
def get_openapi():
    file_path = os.path.join(os.getcwd(), 'openapi.json')
    return FileResponse(file_path, media_type='application/json')

if __name__ == '__main__':
  import uvicorn
  uvicorn.run(app, host='0.0.0.0', port=4000)
