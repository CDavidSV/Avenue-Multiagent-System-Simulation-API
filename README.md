# Avenue Multiagent System Simulation API
 API para el proyecto de un sistema multiagente para visualizar el comportamiento de los vehiculos en una avenida.

Este repositorio es usado en conjunto con el repositorio [RETO-MultiAgentes-UNITY](https://github.com/JCooleyM/RETO-MultiAgentes-UNITY) para la visualización de la simulación.

** Requiere Python 3.11 o superior **

1. Clonar el repositorio
2. Uvicorn no es necesario pero es recomendado para iniciar el servidor.
3. correr `uvicorn app.main:app --host <IP> --port <port>` para iniciar el servidor.

## Required Libraries
- [FastAPI](https://fastapi.tiangolo.com/)
- [Mesa](https://mesa.readthedocs.io/en/stable/)
- [uvicorn](https://www.uvicorn.org/)

## Simulación

| Endpoint                | Metodo | Descripción                                                |
|-------------------------|--------|------------------------------------------------------------|
| `/api/init_sim`         | GET    | Permite la creación de una nueva simulación. Retorna las posiciones iniciales de los vehiculos en la avenida                   |
| `/api/sim_step`         | GET    | Avanza un paso en la simulación especificada       |

### 1. Iniciar una nueva simulación

**Endpoint**: `GET /api/init_sim?cars=<num_cars>&all_lanes=<all_lanes>`

Este endpoint permite la creación de una nueva simulación. Retorna las posiciones iniciales de los vehiculos en la avenida.

**Request:**

- Method: GET

Query Parameters:

`cars=<num_cars>`: Número de vehiculos a simular.
`all_lanes=<all_lanes>`: Si es `true` los vehiculos pueden cambiar de carril.

**Response:**

- Status Code: 200 OK

Respuesta JSON:

```JSON
{
    "sim_id": "ID de la simulación",
    "data": {
        "carr_initial_positions": [
            {
                "id": "ID del vehiculo",
                "pos": {
                    "x": "Posición en x del vehiculo",
                    "y": "Posición en y del vehiculo",
                    "z": "Posición en z del vehiculo"
                },
                ...
            }
        ],
    }
}
```

### 2. Step de la simulación

**Endpoint**: `GET /api/sim_step?sim_id=<sim_id>`

Este endpoint permite avanzar un paso en la simulación especificada.

**Request:**

- Method: GET

Query Parameters:

`sim_id=<sim_id>`: ID de la simulación a avanzar.

**Response:**

- Status Code: 200 OK

JSON Response:

```JSON
{
  "data": {
    "Traffic_Lights": [
      {
        "id": "ID del semaforo",
        "main_lane_state": "El estado del semaforo de la via principal",
        "entry_lane_state": "El estado del semaforo de la via de entrada"
      },
      ...
    ],
    "car_positions": [
      {
        "id": "ID del vehiculo",
        "pos": {
          "x": "Posición en x del vehiculo",
          "y": "Posición en y del vehiculo",
          "z": "Posición en z del vehiculo"
        }
      },
      ...
    ]
  }
}
```