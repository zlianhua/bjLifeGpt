from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from supabase import create_client, Client
from fastapi.middleware.cors import CORSMiddleware
import json  # 引入json模块

SUPABASE_URL = 'https://aauhpkygxsnooxvpqqqy.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFhdWhwa3lneHNub294dnBxcXF5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE2ODc3NTc2MjQsImV4cCI6MjAwMzMzMzYyNH0.kEOf2y2gKWHwHDz2pb3fe11AI8WKosaW5MCwnLhSkwI'
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_origins=["https://chat.openai.com","https://bj-life-gpt.vercel.app"],
  allow_methods=["*"],
  allow_headers=["*"],
  allow_credentials=False
)

class QueryModel(BaseModel):
    table: str
    select: str
    conditions: str
    
class InsertModel(BaseModel):
    table: str
    data: str

class TableModel(BaseModel):
    table: str
    data: str  # 字段名称和类型的JSON字符串

class UpdateModel(BaseModel):
    table: str
    data: str
    conditions: str

class DeleteModel(BaseModel):
    table: str
    conditions: str

@app.get("/")
async def read_root():
    return {"Hello": "World"}     

@app.post("/api/query")
async def query(data: QueryModel):
    query = supabase.table(data.table).select(data.select)
    conditons = data.conditions
    if conditons.strip():
        cond = json.loads(conditons)
        # 这里简化条件处理，具体实现依据conditions内容而定
        for condition in cond:
            column = condition["column"]
            operator = condition["operator"]
            criteria = condition["criteria"]
            # filter 方法调用
            query = query.filter(column, operator, criteria)

    response = query.execute()

    # if response.error:
    #     raise HTTPException(status_code=400, detail=str(response.error))
    return response.data

@app.post("/api/insert")
async def insert(data: InsertModel):
    # 将字符串格式的data.data转换为字典
    dict_data = json.loads(data.data)
    response = supabase.table(data.table).insert(dict_data).execute()

    # if response.error:
    #     raise HTTPException(status_code=400, detail=str(response.error))
    return {"message": "Insert successful", "data": response.data}   
    
@app.post("/api/update")
async def update(data: UpdateModel):
    # 将更新的数据和条件从JSON字符串转换为字典
    update_data = json.loads(data.data)
    update_conditions = json.loads(data.conditions)
    # 构造更新操作的SQL语句
    set_clause = ', '.join([f"{key} = '{value}'" for key, value in update_data.items()])
    condition_clause = ' AND '.join([f"{key} = '{value}'" for key, value in update_conditions.items()])
    sql = f"UPDATE {data.table} SET {set_clause} WHERE {condition_clause};"
    # 执行SQL语句来更新数据
    response = supabase.table(data.table).update(update_data).eq(*update_conditions.items()).execute()
    return response

@app.post("/api/delete")
async def delete(data: DeleteModel):
    # 将删除条件从JSON字符串转换为字典
    delete_conditions = json.loads(data.conditions)
    # 构造删除操作的SQL语句
    condition_clause = ' AND '.join([f"{key} = '{value}'" for key, value in delete_conditions.items()])
    sql = f"DELETE FROM {data.table} WHERE {condition_clause};"
    # 执行SQL语句来删除数据
    response = supabase.table(data.table).delete().match(delete_conditions).execute()
    return response

@app.post("/api/createTable")
async def createTable(data: TableModel):
    # 将字段信息从JSON字符串转换为字典
    fields_dict = json.loads(data.data)
    # 根据提供的字段信息构造表模式
    schema = {}
    for field, properties in fields_dict.items():
        # 这里的properties是一个包含类型和其他选项的字典
        column_type = properties['type']
        # 处理主键
        primary_key = properties.get('primary_key', False)
        # 根据类型创建列
        schema[field] = supabase.types.Column(column_type, primary_key=primary_key)
    
    # 创建表
    response = supabase.table(data.table).create(schema)
    return response

@app.get('/openapi.json')
def get_openapi():
    file_path = os.path.join(os.getcwd(), 'openapi.json')
    return FileResponse(file_path, media_type='application/json')

if __name__ == '__main__':
  import uvicorn
  uvicorn.run(app, host='0.0.0.0', port=4000)
