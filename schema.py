from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker


Base = declarative_base()


class ClienteModel(Base):
   __tablename__ = 'clientes'
  
   id = Column(Integer, primary_key=True, autoincrement=True)
   nombre = Column(String, nullable=False)
   telefono = Column(String)
   email = Column(String)
   fecha_registro = Column(String)
  
   turnos = relationship("TurnoModel", back_populates="cliente", cascade="all, delete-orphan")


class TurnoModel(Base):
   __tablename__ = 'turnos'
  
   id_turno = Column(Integer, primary_key=True, autoincrement=True)
   cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=False)
   servicio = Column(String, nullable=False)
   fecha_hora = Column(DateTime, nullable=False)
   duracion = Column(Integer)
   precio = Column(Float)
   estado = Column(String, default="Confirmado")
  
   cliente = relationship("ClienteModel", back_populates="turnos")


class OperacionesEstetica:
   def __init__(self, db_path="sqlite:///mi_app.db"):
       # Conecta directamente a tu archivo mi_app.db y crea las tablas si no existen
       self.engine = create_engine(db_path, echo=False)
       Base.metadata.create_all(self.engine)
       Session = sessionmaker(bind=self.engine)
       self.session = Session()
      
       self.servicios = {
           "Limpieza facial": {"duracion_min": 60, "precio": 15000},
           "JetPeel": {"duracion_min": 45, "precio": 18000},
           "Dermapen": {"duracion_min": 50, "precio": 22000},
           "Lifting de pestañas": {"duracion_min": 45, "precio": 12000}
       }


   def registrar_cliente(self, nombre, telefono, email=""):
       """Registra una clienta recibiendo los datos como variables normales."""
       nuevo_cliente = ClienteModel(
           nombre=nombre,
           telefono=telefono,
           email=email,
           fecha_registro=datetime.now().strftime("%Y-%m-%d %H:%M")
       )
       self.session.add(nuevo_cliente)
       self.session.commit()
       return {
           "exito": True,
           "mensaje": f"Cliente {nombre} registrado correctamente.",
           "cliente_id": nuevo_cliente.id
       }


   def agendar_turno(self, cliente_id, servicio, fecha_hora_str):
       """Agenda un turno validando el servicio y convirtiendo la fecha."""
       if servicio not in self.servicios:
           return {"exito": False, "error": "El servicio seleccionado no existe."}
      
       try:
           fecha_hora = datetime.strptime(fecha_hora_str, "%Y-%m-%d %H:%M")
       except ValueError:
           return {"exito": False, "error": "Formato de fecha inválido. Utiliza 'AAAA-MM-DD HH:MM'."}


       nuevo_turno = TurnoModel(
           cliente_id=cliente_id,
           servicio=servicio,
           fecha_hora=fecha_hora,
           duracion=self.servicios[servicio]["duracion_min"],
           precio=self.servicios[servicio]["precio"],
           estado="Confirmado"
       )
      
       self.session.add(nuevo_turno)
       self.session.commit()
       return {
           "exito": True,
           "mensaje": "Turno agendado con éxito.",
           "id_turno": nuevo_turno.id_turno
       }


   def listar_turnos_activos(self):
       """Devuelve una lista limpia con los turnos y el nombre de la clienta."""
       turnos = self.session.query(TurnoModel).filter_by(estado="Confirmado").all()
       resultado = []
       for t in turnos:
           resultado.append({
               "id_turno": t.id_turno,
               "cliente": t.cliente.nombre,
               "servicio": t.servicio,
               "fecha_hora": t.fecha_hora.strftime("%Y-%m-d %H:%M"),
               "duracion": t.duracion,
               "precio": t.precio,
               "estado": t.estado
           })
       return resultado


