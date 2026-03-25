
from fastapi.concurrency import asynccontextmanager
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine
from dotenv import load_dotenv
load_dotenv()
import os

# db_url = f"{os.getenv("MY_SQL_USER")}:{os.getenv("MY_SQL_PASSWORD")}@{os.getenv("MY_SQL_HOST")}:{os.getenv("MY_SQL_PORT")/{os.getenv("MY_SQL_DB")}}"
db_url = f"mysql+aiomysql://{os.getenv('MY_SQL_USER')}:{os.getenv('MY_SQL_PASSWORD')}@" \
         f"{os.getenv('MY_SQL_HOST')}:{os.getenv('MY_SQL_PORT')}/{os.getenv('MY_SQL_DB')}"

class Database:
    def __init__(self, db_url: str):
        self.engine = create_async_engine(db_url, echo=False)
        self.async_session = async_sessionmaker(bind=self.engine, class_=AsyncSession, expire_on_commit=False)

    async def init_db(self, engine: AsyncEngine):
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

    async def get_session(self):
        async with self.async_session() as session:
            try:
                yield session
            finally:
                pass
                
    @asynccontextmanager
    async def session_scope(self):
        async with self.async_session() as session:
            yield session
            
            
    # def get_schema_text(self) -> str:
    #     schema_lines = []

    #     for table in SQLModel.metadata.sorted_tables:
    #         schema_lines.append(f"Table: {table.name}")

    #         for column in table.columns:
    #             col_line = f"  - {column.name} ({column.type})"

    #             if column.primary_key:
    #                 col_line += " PRIMARY KEY"

    #             if column.foreign_keys:
    #                 for fk in column.foreign_keys:
    #                     col_line += f" FOREIGN KEY → {fk.target_fullname}"

    #             schema_lines.append(col_line)

    #         schema_lines.append("")  # spacing between tables

    #     return "\n".join(schema_lines)


db = Database(db_url)