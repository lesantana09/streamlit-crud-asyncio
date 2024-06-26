import asyncio
import importlib
import pandas as pd
import streamlit as st
from uuid import uuid4
from sqlalchemy import Column, Integer, String, select
from sqlalchemy.orm import declarative_base

from src.db.base_orm import BaseOrm
from src.db.session_mixin import use_database_session

Base = declarative_base()

class Todo(Base):
    __tablename__ = "todos"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    completed = Column(Integer, default=0)


async def create_tables():
    module = getattr(
        importlib.import_module("src.db.postgres"),
        "PostgresOrm",
    )
    orm_module = module()
    database_uri = orm_module.get_database_uri()
    orm = orm_module.get_orm(base_orm=BaseOrm(database_uri=database_uri))

    with orm.engine.begin() as conn:
        Base.metadata.drop_all(bind=conn)
    
    Base.metadata.create_all(bind=orm.engine)

async def get_todos():
    with use_database_session() as session:
        result = session.scalars(select(Todo))
        todos = result.all()
    return todos

async def create_todo(title: str):
    todo_id = str(uuid4())
    try:
        with use_database_session() as session:
            with session.begin():
                todo = Todo(id=todo_id, title=title)
                session.add(todo)
                session.commit()
        return todo
    except Exception as e:
        print(e)
        raise

async def get_data():
    todos = await get_todos()
    data = [
        {
            "id": todo.id,
            "title": todo.title,
            "completed": todo.completed,
            "delete": False,
        }
        for todo in todos
    ]
    # return pd.DataFrame(data).reset_index(drop=True).set_index("id")
    return pd.DataFrame(data)

async def create_lote_todo():
    titles = [f"Todo:{i}-{uuid4()}" for i in range(50015)]
    tasks = [create_todo(title) for title in titles]
    await asyncio.gather(*tasks)


async def main():    
    st.set_page_config(
        page_title="TODO CRUD",
        page_icon=":white_check_mark:",
        layout="centered",
    )

    data = await get_data()

    st.html(
        """
        <style>
            div[data-testid="column"] {
                width: fit-content !important;
                flex: unset;
            }
            div[data-testid="column"] * {
                width: fit-content !important;
            }
        </style>
        """,
    )

    st.header(" TODO CRUD", divider="rainbow")
    with st.container():
        columns = st.columns([1, 1])
        with columns[0]:
            if st.button("⟳ Refresh"):
                st.rerun()

        with columns[1]:
            with st.popover("➕ New"):
                with st.form("Add TODO", border=False):
                    if st.form_submit_button("Submit"):
                        await create_tables()
                        await create_lote_todo()  

    if not len(data):
        st.warning("No TODOs, add above", icon=":material/warning:")
        st.stop()

    with st.expander("Select visible columns"):
        columns_to_not_show = ["id"]
        filtered_columns_list = list(
            filter(lambda x: x not in columns_to_not_show, list(data.columns))
        )
        selected_columns = st.multiselect(
            "Choose columns",
            options=filtered_columns_list,
            default=filtered_columns_list,
        )

    column_config = {
        "id": None,
        "title": st.column_config.TextColumn(
            "🎯 Title",
        ),
        "completed": st.column_config.CheckboxColumn(
            "✅ Completed",
        ),
        "delete": st.column_config.CheckboxColumn(
            "❌ Delete",
        ),
        # "delete": None,  # Hides Column
    }

    for column in column_config.keys():
        if column not in selected_columns:
            column_config[column] = None

    edited_df = st.data_editor(
        data,
        key="data_editor",
        column_config=column_config,
        use_container_width=True,
        num_rows="fixed",
        hide_index=True,
    )

    data_editor_events = st.session_state.data_editor
    edited_rows = data_editor_events["edited_rows"]

    if not edited_rows:
        return
    for row_position, changed_attributes in edited_rows.items():
        # old_row = data.iloc[row_position]
        new_row = edited_df.iloc[row_position]
        # index = new_row.name # get the field set as index of dataframe
        index = new_row["id"]
        new_row_dict = new_row.to_dict()
        if new_row_dict["delete"]:
            await delete_todo(index)
        else:
            await update_todo(
                id=index,
                title=new_row_dict["title"],
                completed=new_row_dict["completed"],
            )

        st.rerun()

if __name__ == "__main__":
    asyncio.run(main())