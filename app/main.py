from fastapi import FastAPI, HTTPException
from uuid import uuid4
from models.Avenue import Avenue

# Para correr usar: uvicorn app.main:app --host localhost --port 3000 --reload

app = FastAPI()

sims_dict = {}

@app.get("/api/init_sim")
async def initialize_simulation(cars: int, all_lanes: bool):
    # generamos un identificador unico para la simulación creada
    sim_id = str(uuid4())

    # creamos la simulación y la guardamos en el diccionario
    lane_length = 60
    sims_dict[sim_id] = Avenue(all_lanes, cars, lane_length)
    return { "sim_id": sim_id }

@app.get("/api/sim_step")
async def simulation_step(sim_id: str):
    if sim_id not in sims_dict:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    model = sims_dict[sim_id]
    if model.get_car_count() > 0:
        return model.step()
    
    del sims_dict[sim_id]
    return { "message": "Simulation finished" }
