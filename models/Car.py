import mesa

class Car(mesa.Agent):
    def __init__(self, id, model, color, speed, reaction_time):
        super().__init__(id, model)
        self.colors = {1: "red", 2: "blue", 3: "green", 4: "purple"}

        if color not in self.colors:
            raise ValueError(f"Color not allowed. Given: {color}. Allowed: {self.colors.keys()}")

        self.is_moving = True
        self.color = color
        self.speed = speed
        self.reaction_time = reaction_time
        self.curr_iter = 0

        self.direction_deltas = {
            "north": (0, 1),
            "south": (0, -1),
            "east": (1, 0),
            "west": (-1, 0)
        }

    def get_color(self):
        """Retorna el color del carro"""
        return self.colors[self.color]

    def move(self):
        """Mueve el carro en la direccion en la que esta mirando"""
        # Si el carro esta detenido
        if not self.is_moving:
            self.curr_iter += 1

            # Revisamos si en la iteracion actual el carro debe moverse (en base a su tiempo de reaccion)
            if self.curr_iter == self.reaction_time:
                self.is_moving = True
                self.curr_iter = 0
            else: # Si no debe moverse, retornamos
                return

        # Obtener la posicion actual del carro
        x_pos, y_pos = self.pos

        # Revisar si hay un carro en frente. Si lo hay, reducir la velocidad por iteracion
        # Esto revisa cada paso respecto a la velocidad del carro. Por ejemplo, si el carro tiene velocidad 3, se revisa cada celda en frente hasta la 3ra celda
        new_pos = (x_pos, y_pos)
        for _ in range(1, self.speed):
            # Obtener la direccion actual del carro
            direction = self.model.get_direction(new_pos)
            delta_x, delta_y = self.direction_deltas[direction]
            forward_pos = (new_pos[0] + delta_x, new_pos[1] + delta_y)

            # Si nos salimos del grid, no hacer nada
            if self.model.grid.out_of_bounds(forward_pos):
                new_pos = forward_pos
            elif self.model.has_car(forward_pos): # Si hay un carro en frente, intentar cambiar de carril si es posible
                new_pos = self.change_lane(new_pos)
                break # Salir del loop para no seguir avanzando
            elif self.model.is_intersection(forward_pos): # Si hay una interseccion en frente, revisar el semaforo
                traffic_light = self.model.get_traffic_light(forward_pos)
                if traffic_light.get_state(direction) == "red": # Si el semaforo esta en rojo, no avanzar
                    break
                else:
                    new_pos = forward_pos # Si el semaforo esta en verde, avanzar
            else:
                new_pos = forward_pos # Si no hay nada en frente, avanzar 

        # Si la nueva posicion es la misma que la actual, el carro esta detenido
        if new_pos == self.pos:
            self.is_moving = False
            return

        # Si el carro se sale del grid, removerlo
        if self.model.grid.out_of_bounds(new_pos):
            self.model.remove_car(self)
            return

        self.model.grid.move_agent(self, new_pos)

    def change_lane(self, new_pos):
      """Cambia de carril si es posible"""
      xPos, yPos = new_pos
      direction = self.model.get_direction(new_pos)
      if direction == "north" and xPos >= 0 and xPos < 3:
        # Si hay un carro en frente, intentar cambiar de carril
        # Actualizar el contador de iteraciones
        self.curr_iter += 1

        # Si el contador de iteraciones es menor al tiempo de reaccion, no hacer nada
        if self.curr_iter < self.reaction_time:
            return new_pos

        # Obtener los vecinos del carro
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False, radius=3)

        # Filtrar los vecinos del carril derecho y del carril izquierdo
        right_neighbors = list(filter(lambda n: n.pos[0] == xPos + 1, neighbors))
        left_neighbors = list(filter(lambda n: n.pos[0] == xPos - 1, neighbors))

        # Si no hay vecinos en el carril izquierdo, moverse a la izquierda
        if len(left_neighbors) == 0 and len(left_neighbors) <= len(right_neighbors) and xPos > 0:
            xPos -= 1
            self.curr_iter = 0
        elif len(right_neighbors) == 0 and len(right_neighbors) <= len(left_neighbors) and xPos < self.model.grid.width - 1:
            xPos += 1
            self.curr_iter = 0
        # Si no hay vecinos en el carril izquierdo, moverse a la izquierda
        new_pos = (xPos, yPos)
      return new_pos

    def step(self):
        self.move()