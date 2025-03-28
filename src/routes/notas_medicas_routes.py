from fastapi import APIRouter, Depends
from src.controllers.notas_medicas_controller import notasMedicasController
from src.schemas.notas_medicas_schemas import NotaMedicaCreate, NotaMedicaUpdate, NotaMedicaResponse
from src.middleware.role_middleware import RoleRequired

class NotasMedicasRoutes:
    """Clase que maneja las rutas de notas médicas con un patrón Singleton."""

    _instance = None  

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NotasMedicasRoutes, cls).__new__(cls)
            cls._instance.router = APIRouter(prefix="/notas-medicas", tags=["Notas Médicas"])
            cls._instance.initialize_routes()
        return cls._instance

    def initialize_routes(self):
        """Registra los endpoints en el router."""
        self.router.post("/", dependencies=[Depends(RoleRequired(["Administrador","Médico Especialista","Médico General"]))], response_model=dict)(notasMedicasController.crear_nota)
        self.router.get("/multiple", dependencies=[Depends(RoleRequired(["Administrador","Médico Especialista","Médico General"]))], response_model=list)(notasMedicasController.agrupadas_por_diagnostico)
        self.router.get("/{nota_id}", dependencies=[Depends(RoleRequired(["Administrador","Médico Especialista","Médico General"]))], response_model=dict)(notasMedicasController.obtener_nota)
        self.router.get("/", dependencies=[Depends(RoleRequired(["Administrador","Médico Especialista","Médico General"]))], response_model=list)(notasMedicasController.obtener_todas)
        self.router.put("/{nota_id}", dependencies=[Depends(RoleRequired(["Administrador","Médico Especialista","Médico General"]))], response_model=dict)(notasMedicasController.actualizar_nota)
        self.router.delete("/{nota_id}", dependencies=[Depends(RoleRequired(["Administrador","Médico Especialista","Médico General"]))], response_model=dict)(notasMedicasController.eliminar_nota)

# Se obtiene la única instancia de la clase y se usa en FastAPI
notasMedicasRoutes = NotasMedicasRoutes().router
