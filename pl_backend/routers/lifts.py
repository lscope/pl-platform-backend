from datetime import date
from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy import and_
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

from ..models.lift import Lift
from ..models.user import User
from ..dependencies import get_db
from ..oauth2 import get_current_user
from ..routers.users import UserResponse
from ..utils import check_user


SQUAT = "squat"
BENCH = "bench"
DEADLIFT = "deadlift"

PR = "PR"
LAST = "last"
ALL = "all"


# Visto che l'applicazione è strutturata in più moduli python, in ogni router, anziché creare una nuova app FastAPI, creiamo un router dell'app, che poi andremo ad includere nel nostro main
router = APIRouter(
    prefix="/lifts", # endpoint di base di tutti i metodi di questo router
    tags=["Lifts"], # ai soli scopi della documentazione tramite swagger. Questo tag permette di dividere in maniera più chiara e logica le richieste sulla documentazione
)


class LiftType(str, Enum):
    squat = SQUAT
    bench = BENCH
    deadlift = DEADLIFT

# Modello pydantic per validare i dati che ci arrivano nella request (tendenzialmente POST o PUT)
class LiftModel(BaseModel):
    weight: float
    lift_type: LiftType = Field(alias="liftType") # Con Literal[] indichiamo il dominio di input, con alias la chiave effettiva che ci arriva nel json del body della richiesta (così da mantenere il camelCase del json)

    # Necessario creare questa classe per poter leggere dall'alias
    class Config:
        allow_population_by_field_name = True

# Modello pydantic per la response. Definiamo le informazioni che vanno nel body della response
class LiftResponse(BaseModel):
    id: int
    user_id: int
    weight: float
    register_dt: date
    owner: UserResponse # Avendo aggiunto la relazione tra tabella utenti e quella dei pesi recuperiamo tutte le informazioni dell'utente a cui è assegnata l'alzata, e possiamo usare il modello pydantic che abbiamo creato per renderizzarlo in output

    # necessario creare questa classe per specificare che l'oggetto è un oggetto ORM (letto direttamente da DB)
    class Config:
        from_orm = True


@router.get("/{user_id}", response_model=List[LiftResponse]) # Nell'endpoint della richiesta è specificato il PATH_PARAMETER user_id, che possiamo utilizzare all'interno della nostra funzione, richiamandolo tra i parametri. Nell'endpoint tutto è considerato stringa, anche i numeri, quindi per convertirlo in automatico basta utilizzare il type hinting all'interno dei parametri della funzione, e FastAPI automaticamente tenta di fare la conversione, così poi all'interno della funzione possiamo utilizzarlo già nel tipo corretto
def get_user_lifts(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    lift_type: Optional[LiftType] = None,
):
    check_user(user_id, current_user)

    if lift_type is None:
        lifts = db.query(Lift).filter(Lift.user_id == user_id).all()
    else:
        lifts = db.query(Lift).filter(and_(
            Lift.user_id == user_id,
            Lift.lift_type == lift_type,
        )).all()

    return lifts

@router.post("/{user_id}", status_code=status.HTTP_201_CREATED, response_model=LiftResponse) # Abbiamo già impostato lo status code qualora andasse tutto bene. Questo è buona pratica, soprattutto quando è necessario utilizzare status code precisi. In questo caso abbiamo una chiamata POST, quindi che deve creare qualcosa. Se quel qualcosa è stato creato correttamente è bene specificarlo con lo status code 201
def create_lift(user_id: int, lift: LiftModel, db: Session = Depends(get_db), current_user = Depends(get_current_user)): # Una chiamata POST avrà un body con i campi necessari. Per accedervi, FastAPI permette semplicemente di inserire il parametro (del nome che vogliamo - nel nostro caso `lift: LiftModel`) nella definizione della funzione, e specificando il modello pydantic ci viene già parsato con tutti i check, e siamo pronti ad utilizzarlo nella nostra funzione
    check_user(user_id, current_user)

    new_lift = Lift(
        user_id=user_id,
        **lift.model_dump(), # lift è un oggetto pydantic. Se vogliamo un dizionario dobbiamo usare il metodo .model_dump()
    )

    db.add(new_lift) # Aggiungiamo l'utente. Non dobbiamo specificare la tabella, perché SQLAlchemy lo capisce in base all'oggetto creato
    db.commit() # Ogni volta che si fa una modifica al db questa deve essere committata
    db.refresh(new_lift) # Nelle richieste post si restituisce sempre l'oggetto creato (ovviamente togliendo eventuali dati sensibili). Una volta che l'abbiamo creato a DB, facendo un refresh otteniamo il nuovo oggetto creato e possiamo restituirlo

    return new_lift
