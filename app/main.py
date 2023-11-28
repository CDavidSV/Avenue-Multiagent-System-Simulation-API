from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4
from models.Avenue import Avenue

# Para correr usar: uvicorn app.main:app --host localhost --port 3000 --reload

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sims_dict = {}

@app.get("/api/init_sim")
async def initialize_simulation(cars: int, all_lanes: bool):
    # generamos un identificador unico para la simulación creada
    sim_id = str(uuid4())

    # creamos la simulación y la guardamos en el diccionario
    lane_length = 60
    model = Avenue(all_lanes, cars, lane_length)

    # Steps y model
    sims_dict[sim_id] = (0, model)
    
    data = model.get_initial_car_positions()
    return { "sim_id": sim_id, "data": data }

@app.get("/api/sim_step")
async def simulation_step(sim_id: str):
    if sim_id not in sims_dict:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    steps, model = sims_dict[sim_id]
    if model.get_car_count() > 0:
        step_result = model.step()
        steps += 1
        sims_dict[sim_id] = (steps, model)

        return step_result
    
    cars_per_step = model.cars / steps
    total_cars = model.cars

    del sims_dict[sim_id]
    return { "message": "Simulation finished", "total_steps": steps, "cars_per_step": cars_per_step, "car_count": total_cars }