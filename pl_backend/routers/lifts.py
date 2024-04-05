from datetime import date
from fastapi import APIRouter, status, Depends, Response, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, validator
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


# Visto che l'applicazione è strutturata in più moduli python, in ogni router, anziché creare una nuova app FastAPI, creiamo un router dell'app, che poi andremo ad includere nel nostro main
router = APIRouter(
    prefix="/lifts", # endpoint di base di tutti i metodi di questo router
    tags=["Lifts"], # ai soli scopi della documentazione tramite swagger. Questo tag permette di dividere in maniera più chiara e logica le richieste sulla documentazione
)


class LiftType(str, Enum):
    # Classe che indica i valori accettati di un determinato parametro
    squat = SQUAT
    bench = BENCH
    deadlift = DEADLIFT

class RpeValue(float, Enum):
    rpe_0 = 0
    rpe_0_5 = 0.5
    rpe_1 = 1
    rpe_1_5 = 1.5
    rpe_2 = 2
    rpe_2_5 = 2.5
    rpe_3 = 3
    rpe_3_5 = 3.5
    rpe_4 = 4
    rpe_4_5 = 4.5
    rpe_5 = 5
    rpe_5_5 = 5.5
    rpe_6 = 6
    rpe_6_5 = 6.5
    rpe_7 = 7
    rpe_7_5 = 7.5
    rpe_8 = 8
    rpe_8_5 = 8.5
    rpe_9 = 9
    rpe_9_5 = 9.5
    rpe_10 = 10

# Modello pydantic per validare i dati che ci arrivano nella request (tendenzialmente POST o PUT)
class LiftModel(BaseModel):
    weight: float
    lift_type: LiftType = Field(alias="liftType") # Utilizzando il type hinting con la classe LiftType automaticamente facciamo il check con pydantic dei valori accettati di dominio
    rpe: Optional[RpeValue] = Field(default=None)
    notes: Optional[str] = Field(default=None, max_digits=500)

    # Necessario creare questa classe per poter leggere dall'alias
    class Config:
        allow_population_by_field_name = True

    @validator("weight")
    def check_min_weight(self, v):
        if v < 20:
            raise ValueError(f"Minimum weight is 20kg (empty barbell)")

        return v

# Modello pydantic per la response. Definiamo le informazioni che vanno nel body della response
class LiftResponse(BaseModel):
    id: int
    user_id: int = Field(alias="userId")
    weight: float
    rpe: float | None
    notes: str | None
    register_dt: date = Field(alias="registerDt")
    user: UserResponse # Avendo aggiunto la relazione tra tabella utenti e quella dei pesi recuperiamo tutte le informazioni dell'utente a cui è assegnata l'alzata, e possiamo usare il modello pydantic che abbiamo creato per renderizzarlo in output

    # necessario creare questa classe per specificare che l'oggetto è un oggetto ORM (letto direttamente da DB)
    class Config:
        from_orm = True


@router.get("/{user_id}", response_model=List[LiftResponse]) # Nell'endpoint della richiesta è specificato il PATH_PARAMETER user_id, che possiamo utilizzare all'interno della nostra funzione, richiamandolo tra i parametri. Nell'endpoint tutto è considerato stringa, anche i numeri, quindi per convertirlo in automatico basta utilizzare il type hinting all'interno dei parametri della funzione, e FastAPI automaticamente tenta di fare la conversione, così poi all'interno della funzione possiamo utilizzarlo già nel tipo corretto
def get_user_lifts(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    # === Query parameters ===
    lift_type: Optional[LiftType] = None, # Con Optional[LiftType] diciamo a pydantic (che viene chiamato in automatico da FastAPI) che il parametro è opzionale (valore di default None), ma se viene passato deve utilizzare la classe LiftType per identificare i valori ammessi.
    # Inoltre, questo è un QUERY PARAMETER, identificato automaticamente da FastAPI, e il nome del parametro all'interno dell'URL deve essere esattamente quello del parametro
    start_dt: Optional[date] = None,
    end_dt: Optional[date] = None,
    min_weight: Optional[float] = None,
    max_weight: Optional[float] = None,
    min_rpe: Optional[RpeValue] = None,
    max_rpe: Optional[RpeValue] = None,
) -> Lift:
    check_user(user_id, current_user)

    lift_query = db.query(Lift).filter(Lift.user_id == user_id)

    # Filtro per i query parameters passati
    if lift_type is not None:
        lift_query = lift_query.filter(Lift.lift_type == lift_type)
    if start_dt is not None:
        lift_query = lift_query.filter(Lift.register_dt >= start_dt)
    if end_dt is not None:
        lift_query = lift_query.filter(Lift.register_dt <= end_dt)
    if min_weight is not None:
        lift_query = lift_query.filter(Lift.weight >= min_weight)
    if max_weight is not None:
        lift_query = lift_query.filter(Lift.weight <= max_weight)
    if min_rpe is not None:
        lift_query = lift_query.filter(Lift.rpe >= min_rpe)
    if max_rpe is not None:
        lift_query = lift_query.filter(Lift.rpe <= max_rpe)

    lifts = lift_query.all()

    return lifts

@router.post("/{user_id}", status_code=status.HTTP_201_CREATED, response_model=LiftResponse) # Abbiamo già impostato lo status code qualora andasse tutto bene. Questo è buona pratica, soprattutto quando è necessario utilizzare status code precisi. In questo caso abbiamo una chiamata POST, quindi che deve creare qualcosa. Se quel qualcosa è stato creato correttamente è bene specificarlo con lo status code 201
def create_user_lift(
    user_id: int,
    lift: LiftModel,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> Lift: # Una chiamata POST avrà un body con i campi necessari. Per accedervi, FastAPI permette semplicemente di inserire il parametro (del nome che vogliamo - nel nostro caso `lift: LiftModel`) nella definizione della funzione, e specificando il modello pydantic ci viene già parsato con tutti i check, e siamo pronti ad utilizzarlo nella nostra funzione
    check_user(user_id, current_user)

    new_lift = Lift(
        user_id=user_id,
        **lift.model_dump(), # lift è un oggetto pydantic. Se vogliamo un dizionario dobbiamo usare il metodo .model_dump()
    )

    db.add(new_lift) # Aggiungiamo l'utente. Non dobbiamo specificare la tabella, perché SQLAlchemy lo capisce in base all'oggetto creato
    db.commit() # Ogni volta che si fa una modifica al db questa deve essere committata
    db.refresh(new_lift) # Nelle richieste post si restituisce sempre l'oggetto creato (ovviamente togliendo eventuali dati sensibili). Una volta che l'abbiamo creato a DB, facendo un refresh otteniamo il nuovo oggetto creato e possiamo restituirlo

    return new_lift

@router.delete("/{lift_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_lift(
    lift_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    lift = db.query(Lift).filter(Lift.id == lift_id).first()

    if lift is not None:
        check_user(lift.id, current_user) # Se l'alzata esiste, allora controllo che appartenga all'utente corrente
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lift not found")

    db.delete(lift)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{lift_id}", response_model=LiftResponse)
def update_user_lift(
    lift_id: int,
    lift_infos: LiftModel,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Lift:
    lift_query = db.query(Lift).filter(Lift.id == lift_id)
    lift = lift_query.first()

    if lift is not None:
        check_user(lift.id, current_user) # Se l'alzata esiste, allora controllo che appartenga all'utente corrente
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lift not found")

    # Update del peso
    lift_query.update(lift_infos.model_dump(), synchronize_session="fetch")
    db.commit()

    return lift_query.first() # Restituiamo il peso aggiornato
