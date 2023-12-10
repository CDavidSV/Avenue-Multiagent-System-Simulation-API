import mesa

class Car(mesa.Agent):
    def __init__(self, id, model, color, speed, reaction_time):
        super().__init__(id, model)
        self.colors = {1: "red", 2: "blue", 3: "green", 4: "purple"}

        if color not in self.colors:
            raise ValueError(f"Color not allowed. Given: {color}. Allowed: {self.colors.keys()}")
        
        self.car_ahead = False
        self.is_moving = True
        self.color = color
        self.speed = speed
        self.curr_speed = speed
        self.reaction_time = reaction_time
        self.curr_iter_stopped = 0
        self.curr_iter_change_lane = 0

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
            self.curr_iter_stopped += 1

            # Revisamos si en la iteracion actual el carro debe moverse (en base a su tiempo de reaccion)
            if self.curr_iter_stopped >= self.reaction_time:
                self.is_moving = True
                self.curr_iter_stopped = 0
            else: # Si no debe moverse, retornamos
                return

        # Obtener la posicion actual del carro
        x_pos, y_pos = self.pos

        # Revisar si hay un carro en frente. Si lo hay, reducir la velocidad por iteracion
        # Esto revisa cada paso respecto a la velocidad del carro. Por ejemplo, si el carro tiene velocidad 3, se revisa cada celda en frente hasta la 3ra celda
        new_pos = (x_pos, y_pos)
        new_curr_speed = 0
        for _ in range(self.curr_speed):
            # Obtener la direccion actual del carro
            direction = self.model.get_direction(new_pos)
            delta_x, delta_y = self.direction_deltas[direction]
            forward_pos = (new_pos[0] + delta_x, new_pos[1] + delta_y)

            new_curr_speed += 1
            if self.car_ahead and not self.model.has_car(forward_pos):
                self.car_ahead = False

            # Si nos salimos del grid, no hacer nada
            if self.model.grid.out_of_bounds(forward_pos):
                new_pos = forward_pos
            elif self.model.has_car(forward_pos): # Si hay un carro en frente, intentar cambiar de carril si es posible
                self.car_ahead = True
                new_pos = self.change_lane(new_pos)
                break # Salir del loop para no seguir avanzando
            elif self.model.is_intersection(forward_pos): # Si hay una interseccion en frente, revisar el semaforo
                traffic_light = self.model.get_traffic_light(forward_pos)
                if traffic_light.get_state(direction) == "red": # Si el semaforo esta en rojo, no avanzar
                    new_pos = self.change_lane(new_pos)
                    break
                else:
                    new_pos = forward_pos # Si el semaforo esta en verde, avanzar
            else:
                new_pos = forward_pos # Si no hay nada en frente, avanzar

        self.curr_speed = new_curr_speed
        if not self.car_ahead and self.curr_speed < self.speed:
            self.curr_speed += 1

        # Si la nueva posicion es la misma que la actual, el carro esta detenido
        if new_pos == self.pos:
            self.is_moving = False

        # Si el carro se sale del grid, removerlo
        if self.model.grid.out_of_bounds(new_pos):
            self.model.remove_car(self)
            return

        self.model.grid.move_agent(self, new_pos)

    def change_lane(self, new_pos):
        """Intenta cambiar de carril si es posible"""
        xPos, yPos = new_pos

        # Revisar si el carro esta en los carriles de la avenida
        if not (0 <= xPos <= 3):
            return new_pos
        
        self.curr_iter_change_lane += 1
        if self.curr_iter_change_lane < self.reaction_time:
            return new_pos 

        # Obtener los vecinos del carro
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False, radius=10)
        
        # Determinar cual es la distancia al carro mas cercano en cada carril
        left_lane_dist = self.nearest_car_distance(neighbors, xPos - 1) if xPos > self.model.first_lane else 0
        right_lane_dist = self.nearest_car_distance(neighbors, xPos + 1) if xPos < 3 else 0

        # Decidir a que carril moverse
        if left_lane_dist >= right_lane_dist and self.has_enough_space(xPos, yPos, -1) and xPos > self.model.first_lane:
            self.curr_iter_change_lane = 0
            return (xPos - 1, yPos) # Moverse al canal izquierdo
        elif right_lane_dist >= left_lane_dist and self.has_enough_space(xPos, yPos, 1) and xPos < 3:
            self.curr_iter_change_lane = 0
            return (xPos + 1, yPos) # Moverse al canal derecho

        return new_pos

    def nearest_car_distance(self, neighbors, lane_x):
        """Encuentra la distancia al carro mas cercano en el carril dado"""
        lane_cars = [car for car in neighbors if car.pos[0] == lane_x]
        if not lane_cars:
            return float('inf') # No hay carros en el carril
        distances = [abs(car.pos[1] - self.pos[1]) for car in lane_cars]
        return min(distances)
    
    def has_enough_space(self, xPos, yPos, delta):
        """Revisa si el carro tiene suficiente espacio para cambiar de carril"""
        # El valor de delta representa el carril al que queremos cambiar
        # Aqui el carro se encuentra en el centro, Si el delta es -1, significa que queremos que cambie al carril izquierdo (Los cuadros vacios son donde no hay carros)
        # En este ejemplo, el carro no se puede mover a la izquierda porque no hay suficiente espacio
        # □ ■ □
        # □ ■ □ <- Carro actual
        # ■ □ □
        # ■ □ □

        if self.model.has_car((xPos + delta, yPos)):
            return False
        if self.model.has_car((xPos + delta, yPos - 1)):
            return False
        if self.model.has_car((xPos + delta, yPos - 2)):
            return False
        if self.model.has_car((xPos + delta, yPos + 1)):
            return False
        
        return True

    def step(self):
        self.move()