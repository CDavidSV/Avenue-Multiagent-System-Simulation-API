import mesa
import random
from .Car import Car
from .Traffic_Light import Traffic_Light

class Avenue(mesa.Model):
    def __init__(self, all_lanes, cars, main_lane_length = 1000):
        # Esto especifica si se usan todos los carriles
        self.all_lanes = all_lanes
        self.first_lane = 0 if self.all_lanes else 1

        # Variables que manejan los carros y su instanciacion
        self.cars = cars
        self.car_count = 0
        self.car_id = 0
        self.steps_until_next_car = 1
        self.car_obj = []

        # Variables que manejan las entradas a la avenida
        self.main_lane_length = main_lane_length
        self.entry_lane_length = 15
        self.intersections = 2
        self.intersections_pos = []

        # Mesa
        self.id_counter = 0
        self.grid = mesa.space.MultiGrid(3 + self.entry_lane_length, self.main_lane_length, False)
        self.schedule = mesa.time.BaseScheduler(self)
        self.data_collector = mesa.DataCollector(
            model_reporters={"Grid": self.get_grid}
        )

        # Posiciones de las intersecciones
        for i in range(self.intersections):
            # Posicion de la interseccion en la avenida
            y_pos = self.main_lane_length // (self.intersections + 1) * (i + 1)
            x_pos = 3

            self.intersections_pos.append((x_pos, y_pos))

            traffic_light = Traffic_Light(self.get_next_id(), self, "green" if self.id_counter % 2 == 0 else "red")
            self.schedule.add(traffic_light)
            self.grid.place_agent(traffic_light, (x_pos, y_pos))

        # Guardar los carros que seran instanciados en un arreglo
        for i in range(self.cars):
            random_color = random.randint(1, 4) # 1: red, 2: blue, 3: green, 4: yellow
            random_speed = random.randint(1, 3) # elegir una velocidad entre 1 y 3
            random_reaction_time = random.randint(2, 3) # elegir un tiempo de reaccion entre 1 y 3

            lane = random.randint(0, 1) # Decidir si el carro entra por la avenida o por la entrada (1: avenida, 0: entrada)
            if lane == 0:
                random_pos = (self.grid.width - 1, random.choice(self.intersections_pos)[1])
            else:
                random_pos = (random.randint(self.first_lane, 3), 0)

            new_agent = Car(self.get_next_id(), self, random_color, random_speed, random_reaction_time)
            self.car_obj.append((new_agent, random_pos))
        
        self.current_car_index = 0
        self.add_car()
    
    def get_initial_car_positions(self):
        """Retorna un diccionario con las posiciones iniciales de los carros"""
        cars = []
        for obj in self.car_obj:
            cars.append({
                "id": obj[0].unique_id,
                "color": obj[0].color,
                "pos": {
                    "x": obj[1][0],
                    "y": 0,
                    "z": obj[1][1]
                }
            })

        return { "car_initial_positions": cars } 

    def get_direction(self, pos):
        """Retorna la direccion en la que se mueve el carro en la posicion dada"""
        x, _ = pos

        if 3 >= x >= 0: # Retorna la direccion en la avenida
            return "north"
        else: # Retorna la direccion en la entrada
            return "west"

    def get_traffic_light(self, pos):
        """Retorna el semaforo en la posicion dada"""
        agents_at_position = self.grid.get_cell_list_contents([pos])

        # Revisar si hay un semaforo en la posicion
        for agent in agents_at_position:
            if isinstance(agent, Traffic_Light):
                return agent

        return None

    def get_next_id(self):
        """Retorna el siguiente id disponible para un agente"""
        self.id_counter += 1
        return self.id_counter
    
    def get_car_count(self):
        """Retorna la cantidad de carros en la avenida"""
        return self.schedule.get_agent_count() - self.intersections

    def add_car(self):
        """Agrega un carro a la avenida"""
        if self.car_count >= self.cars:
            return

        new_agent, random_pos = self.car_obj[self.current_car_index]
        self.current_car_index += 1
        self.schedule.add(new_agent)
        self.grid.place_agent(new_agent, random_pos)

        # Incrementar el contador de carros
        self.car_count += 1

    def is_intersection(self, pos):
        """Retorna si la posicion dada es una interseccion"""
        # Si la posicion esta en la lista de intersecciones, entonces es una interseccion
        return pos in self.intersections_pos

    def has_car(self, pos):
        """Retorna si la posicion dada tiene un carro"""
        agents_at_position = self.grid.get_cell_list_contents([pos])

        for agent in agents_at_position:
            if isinstance(agent, Car):
                return True

        return False

    def remove_car(self, car_agent):
        """Remueve un carro de la avenida en la posicion dada"""
        self.schedule.remove(car_agent)
        self.grid.remove_agent(car_agent)

    def get_grid(self):
        # Crear una matriz de ceros
        grid = [[0 for _ in range(self.grid.width)] for _ in range(self.grid.height)]

        # Recorrer por todos los agentes y asignar un 1 en la posicion de cada uno
        for cell in self.grid.coord_iter():
            cell_content, (x, y) = cell
            for obj in cell_content:
                if isinstance(obj, Car):
                    grid[y][x] = 1

        return grid

    def get_json_data(self):
        """Retorna un diccionario con los datos del step actual de la simulacion"""
        Traffic_Lights = []
        cars = []

        # Iteramos por todas las celdas del grid
        for cell in self.grid.coord_iter():
            cell_content, (x, y) = cell
            for obj in cell_content:
                if isinstance(obj, Traffic_Light): # Semaforo agregamos su id y sus estados en cada calle
                    Traffic_Lights.append({
                        "id": obj.unique_id,
                        "main_lane_state": obj.main_lane_state,
                        "entry_lane_state": obj.entry_lane_state, 
                    })
                elif isinstance(obj, Car): # Carro agregamos su id y su posicion
                    cars.append({
                        "id": obj.unique_id,
                        "pos": {
                            "x": x,
                            "y": 0,
                            "z": y
                        }
                    })
        
        return { "data": { "Traffic_Lights": Traffic_Lights, "car_positions": cars } } # Retornamos un diccionario con los datos

    def random_step_interval(self):
        """Retorna un numero aleatorio entre 1 y 2 para determinar cada cuantos steps se agrega un carro"""
        return random.randint(1, 2)

    def step(self):
        # Agregar un carro cada cierta cantidad de steps
        self.steps_until_next_car -= 1
        if self.steps_until_next_car <= 0:
            self.steps_until_next_car = self.random_step_interval()
            self.add_car()

        self.data_collector.collect(self)
        self.schedule.step()

        # Retornar los datos de la simulacion
        return self.get_json_data()