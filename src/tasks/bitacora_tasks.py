from redis import Redis
#from rq import Queue
from sqlalchemy.orm import Session
from src.db.db_mysql import databaseMysql
from src.models.index_models import Bitacora  # Asegúrate de tener el modelo
from src.websockets.ws_manager import ws_manager
from src.dao.grupos_sanguineos_dao import grupos_sanguineos_dao

#q = Queue(connection=Redis())

# Variable global para guardar el último ID de bitácora procesado
last_bitacora_id = 0

def revisar_bitacora():
    global last_bitacora_id

    db: Session = next(databaseMysql.get_db())
    try:
        # Obtener el último cambio
        nueva_entrada = db.query(Bitacora).order_by(Bitacora.ID.desc()).first()
        
        if not nueva_entrada:
            return

        if nueva_entrada.ID > last_bitacora_id:
            last_bitacora_id = nueva_entrada.ID

            if nueva_entrada.Tabla == "tbb_personas":
                grupo_sanguineos = grupos_sanguineos_dao.obtener_todos(db)
                ws_manager.broadcast_sync({
                    "message": f"Cambio en personas: {nueva_entrada.Operacion}",
                    "grupo_sanguineo": grupo_sanguineos
                }, ["Administrador"])
    finally:
        db.close()
