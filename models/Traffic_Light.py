import mesa

class Traffic_Light(mesa.Agent):
    def __init__(self, id, model, initial_state, iterations_to_change=90):
        super().__init__(id, model)

        self.state_oposites = {
            "green": "red",
            "red": "green"
        }

        # La ruta principal es la avenida en el eje "y"
        self.main_lane_state = initial_state
        self.entry_lane_state = self.state_oposites[initial_state]
        self.iterations_to_change = iterations_to_change
        self.curr_iter = 0


    def change_state(self):
        """Cambia el estado de los semaforos"""
        self.main_lane_state = self.state_oposites[self.main_lane_state]
        self.entry_lane_state = self.state_oposites[self.entry_lane_state]

    def get_state(self, direction):
        """Retorna el estado del semaforo en la direccion dada"""
        # Retorna su estado dependiendo de la direccion en la que lo mire el carro
        if direction == "north":
            return self.main_lane_state
        elif direction == "west":
            return self.entry_lane_state

    def step(self):
        # Si se llega al numero de iteraciones para cambiar el semaforo, cambiarlo de estado
        if self.curr_iter == self.iterations_to_change:
            self.change_state()
            self.curr_iter = 0
            return

        self.curr_iter += 1