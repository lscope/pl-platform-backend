from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Literal, List

from ..models.lift import Squat, Bench, Deadlift
from ..dependencies import get_db
from ..oauth2 import get_current_user


SQUAT = "squat"
BENCH = "bench"
DEADLIFT = "deadlift"

PR = "PR"
LAST = "last"
ALL = "all"

LIFT_CLASSES = {
    SQUAT: Squat,
    BENCH: Bench,
    DEADLIFT: Deadlift,
}

# Visto che l'applicazione è strutturata in più moduli python, in ogni router, anziché creare una nuova app FastAPI, creiamo un router dell'app, che poi andremo ad includere nel nostro main
router = APIRouter(
    prefix="/lifts", # endpoint di base di tutti i metodi di questo router
    tags=["Lifts"], # ai soli scopi della documentazione tramite swagger. Questo tag permette di dividere in maniera più chiara e logica le richieste sulla documentazione
)


# Modello pydantic per validare i dati che ci arrivano nella request (tendenzialmente POST o PUT)
class LiftModel(BaseModel):
    weight: float
    lift_type: Literal[SQUAT, BENCH, DEADLIFT] = Field(alias="liftType") # Con Literal[] indichiamo il dominio di input, con alias la chiave effettiva che ci arriva nel json del body della richiesta (così da mantenere il camelCase del json)

    # Necessario creare questa classe per poter leggere dall'alias
    class Config:
        allow_population_by_field_name = True

# Modello pydantic per la response. Definiamo le informazioni che vanno nel body della response
class LiftResponse(BaseModel):
    id: int
    user_id: int
    weight: float
    registered_dt: datetime

    # necessario creare questa classe per specificare che l'oggetto è un oggetto ORM (letto direttamente da DB)
    class Config:
        from_orm = True


@router.get("/squats", response_model=List[LiftResponse]) # Specifichiamo il modello pydantic da usare per la response
def get_squats(db: Session = Depends(get_db), user_token = Depends(get_current_user)): # Ogni richiesta che deve lavorare con il db deve avere questo parametro in input, che di fatto recupera l'istanza del db per poterci lavorare, e quando la funzione termina l'istanza del db viene chiusa
    lifts = db.query(Squat).all()

    return lifts # Questo oggetto verrà parsato dal modello della response

@router.get("/squats/{user_id}", response_model=List[LiftResponse]) # Nell'endpoint della richiesta è specificato il PATH_PARAMETER user_id, che possiamo utilizzare all'interno della nostra funzione, richiamandolo tra i parametri. Nell'endpoint tutto è considerato stringa, anche i numeri, quindi per convertirlo in automatico basta utilizzare il type hinting all'interno dei parametri della funzione, e FastAPI automaticamente tenta di fare la conversione, così poi all'interno della funzione possiamo utilizzarlo già nel tipo corretto
def get_user_squats(user_id: int, db: Session = Depends(get_db), user_token = Depends(get_current_user)):
    lifts = db.query(Squat).filter(Squat.user_id == user_id).all()

    return lifts

@router.get("/benches", response_model=List[LiftResponse])
def get_benches(db: Session = Depends(get_db), user_token = Depends(get_current_user)):
    lifts = db.query(Bench).all()

    return lifts

@router.get("/benches/{user_id}", response_model=List[LiftResponse])
def get_user_benches(user_id: int, db: Session = Depends(get_db), user_token = Depends(get_current_user)):
    lifts = db.query(Bench).filter(Bench.user_id == user_id).all()

    return lifts

@router.get("/deadlifts", response_model=List[LiftResponse])
def get_deadlifts(db: Session = Depends(get_db), user_token = Depends(get_current_user)):
    lifts = db.query(Deadlift).all()

    return lifts

@router.get("/deadlifts/{user_id}", response_model=List[LiftResponse])
def get_user_deadlifts(user_id: int, db: Session = Depends(get_db), user_token = Depends(get_current_user)):
    lifts = db.query(Deadlift).filter(Deadlift.user_id == user_id).all()

    return lifts

@router.get("/{user_id}", response_model=List[LiftResponse])
def get_user_lifts(user_id: int, db: Session = Depends(get_db), user_token = Depends(get_current_user)):
    squats = get_user_squats(user_id=user_id)
    benches = get_user_benches(user_id=user_id)
    deadlifts = get_user_deadlifts(user_id=user_id)

    print(squats)
    print(benches)
    print(deadlifts)

    return {}

@router.post("/{user_id}", status_code=status.HTTP_201_CREATED, response_model=LiftResponse) # Abbiamo già impostato lo status code qualora andasse tutto bene. Questo è buona pratica, soprattutto quando è necessario utilizzare status code precisi. In questo caso abbiamo una chiamata POST, quindi che deve creare qualcosa. Se quel qualcosa è stato creato correttamente è bene specificarlo con lo status code 201
def create_lift(user_id: int, lift: LiftModel, db: Session = Depends(get_db), user_token = Depends(get_current_user)): # Una chiamata POST avrà un body con i campi necessari. Per accedervi, FastAPI permette semplicemente di inserire il parametro (del nome che vogliamo - nel nostro caso `lift: LiftModel`) nella definizione della funzione, e specificando il modello pydantic ci viene già parsato con tutti i check, e siamo pronti ad utilizzarlo nella nostra funzione
    lift_model = LIFT_CLASSES[lift.lift_type]

    new_lift = lift_model(
        user_id=user_id,
        **lift.model_dump(), # lift è un oggetto pydantic. Se vogliamo un dizionario dobbiamo usare il metodo .model_dump()
    )

    db.add(new_lift) # Aggiungiamo l'utente. Non dobbiamo specificare la tabella, perché SQLAlchemy lo capisce in base all'oggetto creato
    db.commit() # Ogni volta che si fa una modifica al db questa deve essere committata
    db.refresh(new_lift) # Nelle richieste post si restituisce sempre l'oggetto creato (ovviamente togliendo eventuali dati sensibili). Una volta che l'abbiamo creato a DB, facendo un refresh otteniamo il nuovo oggetto creato e possiamo restituirlo

    return new_lift
