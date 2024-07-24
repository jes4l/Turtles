from tkinter import *
import random
import math
from queue import Queue
import csv

# Making angle more random
def angle_changer(x, y, angle, speed):
    new_x = x + speed * math.cos(angle)
    new_y = y + speed * math.sin(angle)

    return new_x, new_y


class Drawable():
    def __init__(self):
        pass
    def think(self):
        pass
    def draw(self):
        pass


# Conversion Function
def degrees_to_radians(degrees):
    radians = degrees * (math.pi / 180)
    return radians


# Conversion Function
def radians_to_degrees(radians):
    degrees = radians * (180 / math.pi)
    return degrees


# Create Rock
class Rock(Drawable):
    def __init__(self, parent, x, y):
        self.parent = parent
        self.x = x
        self.y = y
        self.size = 20

    def draw(self, canvas: Canvas):
        self.inst = canvas.create_oval(self.x, self.y, self.x + self.size, self.y + self.size, fill = "Sienna4", outline = "Sienna4")

class Light(Drawable):
    def __init__(self, parent, x, y):
        self.parent = parent
        self.x = x
        self.y = y
        self.size = 25
        self.directions = [math.radians(i) for i in range(0, 360, 1)]
        self.lines = []

        light_center_x = self.x + self.size / 2
        light_center_y = self.y + self.size / 2

        for direction in self.directions:
            min_distance = 1000**2
            closest_x = 0
            closest_y = 0
            for wall in self.parent.tiles:
                if isinstance(wall, Rock):
                    pt = self.cast_ray(wall, direction)
                    if pt:
                        distance = (pt[0] - light_center_x)**2 + (pt[1] - light_center_y)**2
                        if min_distance > distance:
                            min_distance = distance
                            closest_x = pt[0]
                            closest_y = pt[1]
            if closest_x and closest_y:
                line = self.parent.canvas.create_line(light_center_x, light_center_y, closest_x, closest_y, fill="lightyellow3")
                self.lines.append(line)
            else:
                end_x = light_center_x + 1000 * math.cos(direction)
                end_y = light_center_y + 1000 * math.sin(direction)
                line = self.parent.canvas.create_line(light_center_x, light_center_y, end_x, end_y, fill="lightyellow3")
                self.lines.append(line)

    def cast_ray(self, wall, direction):
        light_center_x = self.x + self.size / 2
        light_center_y = self.y + self.size / 2

        x3 = light_center_x
        y3 = light_center_y
        x4 = light_center_x + 1000 * math.cos(direction)
        y4 = light_center_y + 1000 * math.sin(direction)

        center_x = wall.x + wall.size / 2
        center_y = wall.y + wall.size / 2
        radius = wall.size / 2

        dx = x4 - x3
        dy = y4 - y3
        a = dx**2 + dy**2
        b = 2 * (dx * (x3 - center_x) + dy * (y3 - center_y))
        c = (x3 - center_x)**2 + (y3 - center_y)**2 - radius**2

        discriminant = b**2 - 4*a*c
        if discriminant >= 0:
            t1 = (-b - math.sqrt(discriminant)) / (2*a)
            t2 = (-b + math.sqrt(discriminant)) / (2*a)
            if 0 <= t1 <= 1:
                ix = x3 + t1 * dx
                iy = y3 + t1 * dy
                return ix, iy
            elif 0 <= t2 <= 1:
                ix = x3 + t2 * dx
                iy = y3 + t2 * dy
                return ix, iy

        return None

    def draw(self, canvas: Canvas):
        try: 
            canvas.delete(self.inst)
        except: 
            pass
        self.inst = canvas.create_oval(self.x, self.y, self.x + self.size, self.y + self.size, fill="lightyellow3", outline="lightyellow3")



# Turtle Class
class Turtle(Drawable):
    def __init__(self, parent, x, y, weight, dirchange, oscilation_factor, size, turtle_number):
        self.weight = weight 
        self.parent = parent
        self.direction_change_value = dirchange
        self.size = size
        self.x = x
        self.y = y 
        self.speed = 0.1
        self.sensor = 0.0 # Water finder
        self.direction = random.uniform(0, 2*math.pi) # Random starting direction
        self.life = 0 # What gen its on
        self.alive = True # If turtle is dead or alive
        self.water = False # If its hit the water
        self.oscilation_factor = oscilation_factor # How much Turtle rotates
        self.clockwise = True
        self.turtle_number = turtle_number # Turtle number
        self.lightray_sensor = 0.0
        self.timer = 0
        self.timer_limit = 500
        self.timer_started = False

        self.ray_hit = -1

        self.think()
        self.positions_facing_rock = []

    def think(self):
        if self.alive == False:
            return
        
        # Turtle Movement
        self.x, self.y = angle_changer(self.x, self.y, self.direction, (self.weight * self.sensor))

        # What gen its at
        self.life +=1

        if(self.life % self.oscilation_factor == 0): self.clockwise = not self.clockwise

        # TODO: maybe make this evolutionary
        direction_scaler = 7

        self.direction = radians_to_degrees(self.direction) # Convert direction

        # tendancy to oscilate based on if it faces water
        # self.sensor is 1 when facing water, 0 when facing away - so (1 - self.sensor) is 1 when facing away, 0 when facing towards
        # here, direction change value is the amount to turn (in degrees), and is multiplied by direction_scaler - which scales the amount to turn by
        # so (1.0 * 7) would mean turn 7 degrees

        # then we multiply this by the (1 - self.sensor)
        # if we are facing the ocean, then self.sensor is 1, (1 - self.sensor) is 0 and (1.0 * 7) * (1 - self.sensor) is 0 - meaning don't turn
        # if we are facing away then self.sensor is 0, (1 - self.sensor) is 1 and (1.0 * 7) * (1- self.sensor) is 7 - meaning turn 7 degrees
        dcv = ((self.direction_change_value * direction_scaler) * (1 - self.sensor)) 
        if(self.clockwise): self.direction = (self.direction + dcv) % 360
        else: self.direction = (self.direction - dcv) % 360
        self.direction = degrees_to_radians(self.direction) # convert direction

        # Direction Turtle is moving
        self.direction_degrees = radians_to_degrees(self.direction) # Convert direction
        self.sensor = ((self.direction_degrees + 270) % 360) / 180
        if self.sensor > 1: self.sensor = 1 - (self.sensor - 1)
        self.sensor = 1 - self.sensor
        if self.y >= 330: # Turtle reach water
            self.alive = False
            self.water = True
            print(f"Turtle {self.turtle_number}, survived because it reached y >= 320")

        if self.life >= 2000: # If it doesnt make it
            self.alive = False
            print(f"Turtle {self.turtle_number}, died because its life reached 2000")
        
        # sense rock
        near_rock = self.sense_rock(list(filter(lambda x: type(x) == Rock, self.parent.tiles)))

        if near_rock and not self.timer_started:
            self.timer_started = True

        if self.timer_started:
            near_rock = True
            self.timer += 1

        if self.timer >= self.timer_limit:
            self.timer = 0
            self.timer_started = False

        if not near_rock:
            # sense light
            self.sense_lightray(list(filter(lambda x: type(x) == Light, self.parent.items)))   

    def line_intersects_oval(self, line_coords):
        x1, y1, x2, y2 = line_coords

        if x1 == x2 : return False
        x_center = self.x
        y_center = self.y
        x_radius = self.size
        y_radius = self.size

        if y2 > y_center: return False


        # Compute the equation of the line: y = mx + b
        m = (y2 - y1) / (x2 - x1)
        b = y1 - m * x1

        # Check if any of the four corners of the bounding box of the oval lies on the line
        for corner_x, corner_y in [(x_center - x_radius, y_center - y_radius),
                                    (x_center + x_radius, y_center - y_radius),
                                    (x_center - x_radius, y_center + y_radius),
                                    (x_center + x_radius, y_center + y_radius)]:
            if abs(corner_y - (m * corner_x + b)) < 0.0001:
                return True

        # Compute the distance between the center of the oval and the line
        distance = abs(y_center - (m * x_center + b)) / ((m ** 2 + 1) ** 0.5)

        # Check if the distance is less than or equal to the radius of the oval
        if distance <= x_radius or distance <= y_radius:
            return True

        return False
    
    def sense_lightray(self, lights):
    # Make the light ray change oscilation factor 
        for light in lights:
            for line in light.lines:

                line_coords = self.parent.canvas.coords(line)
                
                if(self.line_intersects_oval(line_coords)):

                    self.parent.hit_lines.append(line)
                    

                    if self.ray_hit != line:
                        self.lightray_sensor = 1
                        self.ray_hit = line
                else: 
                    self.lightray_sensor = 0


                if(self.lightray_sensor == 1):
                    # find out the angle between the start and end point

                    start_x = self.x
                    start_y = self.y

                    dest_x = line_coords[0]
                    dest_y = line_coords[1]

                    dx = dest_x - start_x
                    dy = dest_y - start_y

                     # Calculate the angle using arctangent (atan2)
                    angle_rad = math.atan2(dy, dx)

                    self.direction = angle_rad
                    return
                
    def sense_rock(self, rocks):

        for rock in rocks:
            # Put rock centre tile
            rock_center_x = rock.x + rock.size / 2
            rock_center_y = rock.y + rock.size / 2

            # Put turtle centre tile
            turtle_center_x = self.x + self.size / 2
            turtle_center_y = self.y + self.size / 2

            # Calculate the distance from the center of the turtle to the center of the rock
            distance = math.sqrt((turtle_center_x - rock_center_x)**2 + (turtle_center_y - rock_center_y)**2)

            # Limiting factor, T dies when to close to rock
            if distance < 13:
                self.alive = False
                print("Turtle {self.turtle_number}, died by Rock collision")
                return True

            if distance < 17:
                # Angle between the turtle and the rock
                angle = math.atan2(rock_center_y - turtle_center_y, rock_center_x - turtle_center_x)

                # Adjust the turtle's direction to be the opposite of this angle
                if(self.clockwise): self.direction = angle + math.pi
                else: self.direction = angle - math.pi
                self.positions_facing_rock.append((self.x, self.y))  # store position
                return True
            
        return False

    # Remove last Frame
    def draw(self, canvas: Canvas):
        try: 
            canvas.delete(self.inst)
            canvas.delete(self.dir_inst)
            canvas.delete(self.turtle_number_inst)
        except: 
            pass
        
        # Turtle
        self.inst = canvas.create_oval(self.x, self.y, self.x + self.size, self.y + self.size, fill = "green" if self.alive else "red" if not self.water else "aqua")
        
        # Head
        dir_x = self.x + self.size/2 + self.size/2 * math.cos(self.direction)
        dir_y = self.y + self.size/2 + self.size/2 * math.sin(self.direction)
        self.dir_inst = canvas.create_line(self.x + self.size/2, self.y + self.size/2, dir_x, dir_y, fill = "red")
        
        # Turtle number
        self.turtle_number_inst = canvas.create_text(self.x, self.y - 20, text=f"{self.turtle_number}", fill="black")

class Bird(Drawable):
    def __init__(self, parent, x, y, weight, bird_number):
        self.weight = weight
        self.parent = parent
        self.size = 10
        self.x = x
        self.y = y
        self.speed = 1
        self.life = 0 # What gen its on
        self.alive = True
        self.direction = random.uniform(0, 2*math.pi)
        self.sensing_range = 100
        self.detected_turtles = set()  # Store detected turtles
        self.bird_number = bird_number
        self.eaten = 0

    def think(self):
        if self.alive == False:
            return
        
        # Bird's erratic flight pattern
        self.direction += random.uniform(-math.pi / 8, math.pi / 8)
        self.direction %= 2*math.pi
        self.x, self.y = angle_changer(self.x, self.y, self.direction, self.weight)
        self.x = self.x % 800
        self.y = self.y % 500
        # What gen its at
        
        self.life +=1
        if self.life >= 2000: # If it doesnt make it
            self.alive = False
            print(f"Bird died at {self.bird_number} because its life reached 2000")

        self.sense_turtle()

        # Check if all turtles are dead
        if self.all_dead():
            self.alive = False
            print(f"Bird died at {self.bird_number} because turtles died")

    def sense_turtle(self):
        for item in self.parent.items:
            if isinstance(item, Turtle) and item.alive:
                # Calculate distance between bird and turtle
                distance = math.sqrt((self.x - item.x)**2 + (self.y - item.y)**2)
                # Calculate angle between bird's direction and turtle
                angle_to_turtle = math.atan2(item.y - self.y, item.x - self.x)
                angle_difference = abs(self.direction - angle_to_turtle)
                angle_difference = min(angle_difference, 2*math.pi - angle_difference)  # Normalize to be within 0 to pi

                # Adjust the sensing range based on the size of the turtle
                adjusted_sensing_range = self.sensing_range if item.size >= 10 else self.sensing_range / 2

                # If the turtle is within sensing range and facing the bird's direction
                if distance <= adjusted_sensing_range and angle_difference < math.pi / 4:
                    if item not in self.detected_turtles:
                        print(f"Turtle {item.turtle_number} detected in bird {self.bird_number} path!")
                        self.detected_turtles.add(item)

                    # Move towards the turtle
                    self.direction = math.atan2(item.y - self.y, item.x - self.x)
                    self.x, self.y = angle_changer(self.x, self.y, self.direction, self.speed)

                    # Check for collision with the turtle
                    if distance <= self.size / 2 + item.size / 2:
                        item.alive = False
                        item.water = False
                        print(f"Turtle {item.turtle_number} killed by bird {self.bird_number}")
                        self.detected_turtles.remove(item)
                        self.eaten += 1

    def draw(self, canvas: Canvas):
        # remove last frame if exists!
        try:
            canvas.delete(self.inst)
            canvas.delete(self.dir_inst)
            canvas.delete(self.bird_number_inst)
        except:
            pass

        self.inst = canvas.create_oval(self.x, self.y, self.x + self.size, self.y + self.size, fill="Black" if self.alive else "red")

        # direction facing
        dir_x = self.x + self.size / 2 + self.size / 2 * math.cos(self.direction)
        dir_y = self.y + self.size / 2 + self.size / 2 * math.sin(self.direction)
        self.dir_inst = canvas.create_line(self.x + self.size / 2, self.y + self.size / 2, dir_x, dir_y, fill="red")

        # Bird number
        self.bird_number_inst = canvas.create_text(self.x, self.y - 20, text=f"{self.bird_number}", fill="black")

    def all_dead(self):
        all_turtles = [turtle for turtle in self.parent.items if isinstance(turtle, Turtle)]
        return all(not turtle.alive for turtle in all_turtles)

class Sea(Drawable):
    def __init__(self, parent, x, y):
        self.parent = parent
        self.x = x
        self.y = y
        self.size = 20
        
    def draw(self, canvas: Canvas):
        self.inst = canvas.create_rectangle(self.x, self.y, self.x + self.size, self.y + self.size, fill = "midnightblue", outline = "midnightblue")


class Window():
    def __init__(self, map):
        self.state = 3
        self.all_dead_message_printed_bird = False

        self.hit_lines = []

        self.master = Tk()
        self.master.geometry("1600x500") # Adjust the size as needed
        self.iteration = 0

        # Create a frame for the simulation
        self.simulation_frame = Frame(self.master)
        self.simulation_frame.place(x = 0, y = 0, width = 800, height = 500)

        # Create a frame for the turtle information
        self.info_frame = Frame(self.master)
        self.info_frame.place(x = 800, y = 20, width = 800, height = 500) 
        
        # Create a frame for the buttons
        self.button_frame = Frame(self.info_frame)

        # Create Play button
        self.play_button = Button(self.button_frame, text = "Play", command = self.play)
        self.play_button.pack(side = LEFT)

        # Create Pause button
        self.pause_button = Button(self.button_frame, text = "Pause", command = self.pause)
        self.pause_button.pack(side = LEFT)

        # Create Toggle button
        self.toggle_button = Button(self.button_frame, text = "Variant of Elitist Selection", command = self.toggle_state)
        self.toggle_button.pack(side = LEFT)

        # Create a label for the iteration
        self.iteration_label = Label(self.button_frame, text=f"Generation: {self.iteration}")
        self.iteration_label.pack(side=LEFT)

        self.canvas = Canvas(self.simulation_frame, height = 500, width = 800, background = "DarkGoldenrod3")
        self.canvas.pack()

        # Get the number of rows in the info_frame
        max_rows = 12
        num_rows = max_rows * 2

        # Place the button_frame at the bottom of the info_frame
        self.button_frame.grid(row=num_rows, column=0, columnspan=3, sticky="ew")
        self.info_frame.grid_rowconfigure(num_rows, weight=1)
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_rowconfigure(0, weight=1)

        self.items = []
        self.all_dead_message_printed = False

        self.map = map
        self.tiles = []

        # Create Rock instances for each rock in the map
        for i in range(len(self.map)):
            for j in range(len(self.map[i])):
                if self.map[i][j] == 1:
                    self.tiles.append(Rock(self, j * 20, i * 20))
                elif self.map[i][j] == 2:
                    self.tiles.append(Sea(self, j * 20, i * 20))

        for tile in self.tiles:
            tile.draw(self.canvas)

        # Add a flag to indicate whether the simulation is running or not
        self.running = True

        num_turtles = 12
        num_columns = 6  # Set the number of columns directly
        max_rows = math.ceil((num_turtles + 6) / num_columns)  # Calculate the number of rows needed turtle+bird num

        # Define the line segment range
        line_start_x = 100
        line_end_x = 750

        # Define the number of segments
        num_segments = random.randint(6, 10)
        segment_width = (line_end_x - line_start_x) // num_segments

        self.turtle_info_texts = []
        for x in range(num_turtles):
            # Randomly select a segment for the turtle to spawn in
            segment_index = random.randint(0, num_segments - 1)
            
            # Calculate the x-coordinate within the selected segment
            segment_start = line_start_x + segment_index * segment_width
            segment_end = segment_start + segment_width
            turtle_x = random.randint(segment_start, segment_end)

            turtle = Turtle(self,                               # parent
                            turtle_x,                           # random x co ordinate within the segment
                            100,                                # y position
                            random.randrange(0, 100) / 100,     # random weight for the turtle btw 0 - 1
                            random.randrange(0, 300) / 100,     # random direction change
                            random.randrange(10, 30),           # osiclation factor
                            random.randrange(500, 1500) / 100,  # turtle size
                            x + 1)                              # turtle number
            
            self.items.append(turtle)

            # Create label for each turtle
            turtle_label = Label(self.info_frame, text = f"Turtle {x + 1}")
            turtle_label.grid(row = x % max_rows * 2, column = x // max_rows, padx = 5, pady = 2, sticky = "w")
    
            # Create text widget for each turtle info
            turtle_text = Text(self.info_frame, height = 8, width = 22, font=("Helvetica", 7))
            turtle_text.grid(row = x % max_rows * 2 + 1, column=x // max_rows, padx = 5, pady = 2, sticky = "w")
            self.turtle_info_texts.append(turtle_text)

        num_birds = 6

        bird_line_start_y = 50
        bird_line_end_y = 750    

        bird_num_segments = random.randint(2,5)
        bird_segment_width = (bird_line_end_y - bird_line_start_y) // bird_num_segments

        self.bird_info_texts = []
        for y in range(num_birds):
            # Randomly select a segment for the turtle to spawn in
            bird_segment_index = random.randint(0, bird_num_segments - 1)

            # Calculate the x-coordinate within the selected segment
            bird_segment_start = bird_line_start_y + bird_segment_index * bird_segment_width
            bird_segment_end = bird_segment_start + bird_segment_width
            bird_y = random.randint(bird_segment_start, bird_segment_end)

            bird = Bird(self,                               # parent
                        bird_y,                             # x coordinate
                        300,                                 # y coordinate
                        random.randrange(0, 100) / 100,     # random weight for the bird btw 0 - 1
                        y + 1)                               # bird number

            self.items.append(bird)

            # Create label for each bird
            bird_label = Label(self.info_frame, text=f"Bird {y + 1}")
            bird_label.grid(row=(num_turtles + y) % max_rows * 2, column=(num_turtles + y) // max_rows, padx=5, pady=5, sticky="w")

            # Create text widget for each bird info
            bird_text = Text(self.info_frame, height=8, width=20, font=("Helvetica", 7))  # Adjust the height and width as needed
            bird_text.grid(row=(num_turtles + y) % max_rows * 2 + 1, column=(num_turtles + y) // max_rows, padx=5, pady=5, sticky="w")
            self.bird_info_texts.append(bird_text)

        for z in range(0, 1):
            light = Light(self,
                                    400,
                                    470)
            self.items.append(light)

        while True:
            self.mainloop()
    
    def export_data_to_csv(self):
        file_name = "data.csv"
        headers = ["State", "Iteration", "Average Turtle Life", "Average Turtle Size", "Average Direction", "Oscillation", "Average Turtle Weight", "", "State", "Iteration", "Average Bird Life", "Average Bird Weight", "Average Turtles Eaten"]
        
        # Calculate averages for turtles
        all_turtles = [turtle for turtle in self.items if isinstance(turtle, Turtle)]
        avg_turtle_life = sum(turtle.life for turtle in all_turtles) / len(all_turtles)
        avg_turtle_size = sum(turtle.size for turtle in all_turtles) / len(all_turtles)
        avg_turtle_direction = sum(turtle.direction_change_value for turtle in all_turtles) / len(all_turtles)
        avg_turtle_weight = sum(turtle.weight for turtle in all_turtles) / len(all_turtles)
        avg_turtle_Oscilation = sum(turtle.oscilation_factor for turtle in all_turtles) / len(all_turtles)

        # Calculate averages for birds
        all_birds = [bird for bird in self.items if isinstance(bird, Bird)]
        avg_bird_life = sum(bird.life for bird in all_birds) / len(all_birds)
        avg_bird_weight = sum(bird.weight for bird in all_birds) / len(all_birds)
        avg_turtles_eaten = sum(bird.eaten for bird in all_birds) / len(all_birds)
        
        # Determine the state
        if self.state == 1:
            state = "Tournament Selection"
        elif self.state == 2:
            state = "Steady State Selection"
        else:  # self.state == 3
            state = "Variant of Elitist Selection"
        
        # Print iteration and averages to console
        print(f"Iteration: {self.iteration}, Average Turtle Life: {avg_turtle_life}, Average Turtle Size: {avg_turtle_size}, Average Direction: {avg_turtle_direction}, Average Turtle Weight: {avg_turtle_weight}, Average Bird Life: {avg_bird_life}, Average Oscillation: {avg_turtle_Oscilation} Average Bird Weight: {avg_bird_weight}, Average Turtles Eaten: {avg_turtles_eaten}")
        
        # Write data to CSV file
        with open(file_name, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(headers) if file.tell() == 0 else None
            writer.writerow([state, self.iteration, avg_turtle_life, avg_turtle_size, avg_turtle_direction, avg_turtle_Oscilation , avg_turtle_weight, "", "", state, self.iteration, avg_bird_life, avg_bird_weight, avg_turtles_eaten])
        
        print("Data updated in data.csv")


    def play(self):
        # Set the running flag to True to resume the simulation
        self.running = True

    def pause(self):
        # Set the running flag to False to pause the simulation
        self.running = False

    def toggle_state(self):
        # Cycle the state variable between 1, 2, and 3
        self.state = 1 if self.state == 3 else self.state + 1

        # Update the text of the toggle button to reflect the current state
        if self.state == 1:
            self.toggle_button.config(text="Tournament Selection")
        elif self.state == 2:
            self.toggle_button.config(text="Steady State Selection")
        else:  # self.state == 3
            self.toggle_button.config(text="Variant of Elitist Selection")


    # Check if all turtles are dead
    def all_dead(self):
        all_turtles = [item for item in self.items if isinstance(item, Turtle)]
        all_birds = [item for item in self.items if isinstance(item, Bird)]
        
        if all(not turtle.alive for turtle in all_turtles) and all(not bird.alive for bird in all_birds):
            if not self.all_dead_message_printed:
                print("All turtles and birds are dead.")
                self.export_data_to_csv()
                self.all_dead_message_printed = True
            return True
        return False

    def mainloop(self):
        if self.running:
            for item in self.items:
                item.think()
            for item in self.items:
                item.draw(self.canvas)
            
            for light in filter(lambda i: type(i) == Light, self.items):
                    for line in light.lines:
                        if line in self.hit_lines:
                            self.canvas.itemconfigure(line, fill="green")
                        else:
                            self.canvas.itemconfigure(line, fill="lightyellow3")
        self.hit_lines = []

        # Update Iteration
        self.iteration_label.config(text=f"Generation: {self.iteration}")
        self.master.update()

        # Update turtle info text widgets
        for i, turtle in enumerate(filter(lambda i: isinstance(i, Turtle), self.items)):
            if turtle.alive:
                if turtle.water:
                    alive_status = f"Turtle {i + 1} survived"
                    colour = "green" # Green for survived
                else:
                    alive_status = f"Turtle {i + 1} is alive"
                    colour = "black" # Black for alive
            else:
                if turtle.water:
                    alive_status = f"Turtle {i + 1} survived"
                    colour = "green" # Green for survived
                else:
                    alive_status = f"Turtle {i + 1} died"
                    colour = "red" # Red for died

            turtle_info = f"Direction: {round(turtle.sensor, 3)}\nLife: {turtle.life}\nSize: {round(turtle.size, 3)}\nOscillation Fac: {round(turtle.oscilation_factor, 3)}\nDir Change: {round(turtle.direction_change_value, 3)}\nStatus: {alive_status}\nWeight: {round(turtle.weight, 3)}\nPosition: (x {round(turtle.x)}, y {round(turtle.y)})"

            # Update text widget for each turtle info
            self.turtle_info_texts[i].delete(1.0, "end")
            self.turtle_info_texts[i].insert("end", turtle_info)

            # Change the colour of the status line
            self.turtle_info_texts[i].tag_add("status", "6.0", "6.end")
            self.turtle_info_texts[i].tag_config("status", foreground = colour)

        # Update bird info text widgets
        for i, bird in enumerate(filter(lambda i: isinstance(i, Bird), self.items)):
            if bird.alive:
                alive_status = f"Bird {i + 1} is alive"
                colour = "black" # Black for alive
            else:
                alive_status = f"Bird {i + 1} died"
                colour = "red" # Red for died

            bird_info = f"Direction: {round(bird.direction, 3)}\nLife: {bird.life}\nWeight: {round(bird.weight, 3)}\nPosition: (x {round(bird.x)}, y {round(bird.y)}\nStatus: {alive_status}\nEaten: {bird.eaten}"

            # Update text widget for each bird info
            self.bird_info_texts[i].delete(1.0, "end")
            self.bird_info_texts[i].insert("end", bird_info)

            # Change the colour of the status line
            self.bird_info_texts[i].tag_add("status", "5.0", "5.end")
            self.bird_info_texts[i].tag_config("status", foreground = colour)

        # stores values for evolution
        if self.all_dead():
            if self.state == 1:
                print("Tournament Selection")
                size_list = []
                weight_list = []
                direction_list = []
                oscilation_list = []

                weight_list_bird = []
                
                self.iteration += 1
                self.all_dead_message_printed = False
                print("Iteration: ", self.iteration)

                # get surviving turtles, and get their weights (if there are no survivors, put randoms)
                surviving_turtles2 = list(filter(lambda i: type(i) == Turtle, self.items))
                print("Number of surviving turtles: ", len(surviving_turtles2))

                # break into 3 subgroups
                grp1 = []
                grp2 = []
                grp3 = []

                try:
                    while True:
                        grp1.append(surviving_turtles2.pop(0))
                        grp2.append(surviving_turtles2.pop(0))
                        grp3.append(surviving_turtles2.pop(0))
                except:
                    pass

                print("Number of surviving turtles in all groups: ", len(grp1) + len(grp2) + len(grp3))

                grp1 = sorted(grp1, key=lambda i: i.life)
                grp2 = sorted(grp2, key=lambda i: i.life)
                grp3 = sorted(grp3, key=lambda i: i.life)
                print("GROUPS ::")
                print(str(grp1) + " 1 " + str(grp2) + " 2 " + str(grp3) + " 3")
                
                surviving_turtles = list(filter(lambda i: type(i) == Turtle, self.items))
                surviving_turtles = sorted(surviving_turtles, key=lambda i: i.life)
                surviving_turtles[0] = grp1[0]
                surviving_turtles[1] = grp2[0]
                surviving_turtles[2] = grp3[0]

                weight_list.append(surviving_turtles[0].weight)
                weight_list.append(surviving_turtles[1].weight)
                weight_list.append(surviving_turtles[2].weight)

                direction_list.append(surviving_turtles[0].direction_change_value)
                direction_list.append(surviving_turtles[1].direction_change_value)
                direction_list.append(surviving_turtles[2].direction_change_value)

                oscilation_list.append(surviving_turtles[0].oscilation_factor)
                oscilation_list.append(surviving_turtles[1].oscilation_factor)
                oscilation_list.append(surviving_turtles[2].oscilation_factor)

                size_list.append(surviving_turtles[0].size)
                size_list.append(surviving_turtles[1].size)
                size_list.append(surviving_turtles[2].size)


                # Get all birds that have eaten at least one turtle
                Birds_that_have_eaten2 = list(filter(lambda i: type(i) == Bird, self.items))
                print("Number of surviving bird: ", len(Birds_that_have_eaten2))

                # break into 3 subgroups
                bird_grp1 = []
                bird_grp2 = []
                bird_grp3 = []

                try:
                    while True:
                        bird_grp1.append(Birds_that_have_eaten2.pop(0))
                        bird_grp2.append(Birds_that_have_eaten2.pop(0))
                        bird_grp3.append(Birds_that_have_eaten2.pop(0))
                except:
                    pass

                print("Number of best birds in all groups: ", len(bird_grp1) + len(bird_grp2) + len(bird_grp3))


                bird_grp1 = sorted(bird_grp1, key=lambda i: i.life)
                bird_grp2 = sorted(bird_grp2, key=lambda i: i.life)
                bird_grp3 = sorted(bird_grp3, key=lambda i: i.life)
                print("GROUPS ::")
                print(str(bird_grp1) + " 1 " + str(bird_grp2) + " 2 " + str(bird_grp3) + " 3")
              
                Birds_that_have_eaten = list(filter(lambda i: type(i) == Bird, self.items))
                Birds_that_have_eaten = sorted(Birds_that_have_eaten, key=lambda i: i.eaten, reverse=True)
                Birds_that_have_eaten[0] = bird_grp1[0]
                Birds_that_have_eaten[1] = bird_grp2[0]
                Birds_that_have_eaten[2] = bird_grp3[0]

                weight_list_bird.append(Birds_that_have_eaten[0].weight)
                weight_list_bird.append(Birds_that_have_eaten[1].weight)
                weight_list_bird.append(Birds_that_have_eaten[2].weight)
                    
                    
                # Delete all tiles (rocks and sea)
                for tile in self.tiles:
                    self.canvas.delete(tile.inst)

                # make new map and rocks
                self.map = []
                self.map = create_map(40, 25)
                self.tiles = []
                for i in range(len(self.map)):
                    for j in range(len(self.map[i])):
                        if self.map[i][j] == 1:
                            self.tiles.append(Rock(self, j * 20, i * 20))
                        elif self.map[i][j] == 2:
                            self.tiles.append(Sea(self, j * 20, i * 20))
                for tile in self.tiles:
                    tile.draw(self.canvas)

                # delete all turtles
                for turtle in filter(lambda i: type(i) == Turtle, self.items):
                    self.canvas.delete(turtle.inst)
                    self.canvas.delete(turtle.dir_inst)
                    self.canvas.delete(turtle.turtle_number_inst)

                # delete all birds
                for bird in filter(lambda i: type(i) == Bird, self.items):
                    self.canvas.delete(bird.inst)
                    self.canvas.delete(bird.dir_inst)
                    self.canvas.delete(bird.bird_number_inst)

                # delete light and light lines
                for light in filter(lambda i: type(i) == Light, self.items):
                    self.canvas.delete(light.inst)
                    for line in light.lines:
                        self.canvas.delete(line)
                    light.lines.clear()

                # Define the number of segments
                num_segments = random.randint(6, 10)

                # Define the line segment range
                line_start_x = 100
                line_end_x = 750
                segment_width = (line_end_x - line_start_x) // num_segments

                # respawn new turtles with mutated weights
                self.items = list(filter(lambda i: type(i) != Turtle, self.items))
                for x in range(12):
                    # Randomly select a segment for the turtle to spawn in
                    segment_index = random.randint(0, num_segments - 1)
                    # Calculate the x-coordinate within the selected segment
                    segment_start = line_start_x + segment_index * segment_width
                    segment_end = segment_start + segment_width
                    turtle_x = random.randint(segment_start, segment_end)

                    random_minus10_to_10 = random.randrange(-100, 100) / 1000
                    weight = weight_list[random.randrange(0, len(weight_list))] + random_minus10_to_10
                    dir = direction_list[random.randrange(0, len(weight_list))] + random_minus10_to_10
                    osc = oscilation_list[random.randrange(0, len(oscilation_list))] + (random_minus10_to_10 * 100) / 3
                    siz = size_list[random.randrange(0, len(size_list))] + (random_minus10_to_10 * 2)
                    self.items.append(Turtle(self, turtle_x, 100, weight, dir, osc, siz, x + 1))
                    
                # Define the number of segments
                bird_num_segments = random.randint(2,5)

                # Define the line segment range
                bird_line_start_y = 100
                bird_line_end_y = 750
                bird_segment_width = (bird_line_end_y - bird_line_start_y) // bird_num_segments

                # respawn new birds with mutated weights
                self.items = list(filter(lambda i: type(i) != Bird, self.items))
                for y in range(0, 6):
                    # Randomly select a segment for the turtle to spawn in
                    bird_segment_index = random.randint(0, bird_num_segments - 1)
                    # Calculate the x-coordinate within the selected segment
                    bird_segment_start = bird_line_start_y + bird_segment_index * bird_segment_width
                    bird_segment_end = bird_segment_start + bird_segment_width
                    bird_y = random.randint(bird_segment_start, bird_segment_end) 

                    random_minus10_to_10 = random.randrange(-100, 100) / 1000
                    weight = weight_list_bird[random.randrange(0, len(weight_list_bird))] + random_minus10_to_10
                    self.items.append(Bird(self, bird_y, 300, weight, y + 1))
                

                # respawn light
                self.items = list(filter(lambda i: type(i) != Light, self.items))
                for y in range(0,1):
                    self.items.append(Light(self, 400, 470))
                
            elif self.state == 2:
                print("Steady State Selection")

                self.iteration += 1
                self.all_dead_message_printed = False
                print("Iteration: ", self.iteration)

                all_turtles = list(filter(lambda i: type(i) == Turtle, self.items))
                best_turtles = sorted(filter(lambda i: type(i) == Turtle and i.water == True, all_turtles), key=lambda i: i.life, reverse=True)[:3]
                
                # Find the worst turtles (those that have not reached the water)
                worst_turtles = sorted(filter(lambda turtle: isinstance(turtle, Turtle) and not turtle.water, all_turtles), key=lambda turtle: turtle.life)[:3]

                # If there are no worst turtles (all turtles have reached the water)
                # select the 3 turtles with the highest life that made it to water
                if not worst_turtles:
                    worst_turtles = sorted(filter(lambda turtle: isinstance(turtle, Turtle) and turtle.water, all_turtles), key=lambda turtle: turtle.life, reverse=True)[:3]

                # If there are no best turtles, generate random attributes for all turtles
                if not best_turtles:
                    for turtle in all_turtles:
                        turtle.weight = random.randrange(0, 100) / 100
                        turtle.direction_change_value = random.randrange(0, 300) / 100
                        turtle.oscilation_factor = random.randrange(10, 30)
                        turtle.size = random.randrange(0, 12)
                else:
                    # Replace the attributes of the worst turtles with those of the best turtles
                    for i, worst_turtle in enumerate(worst_turtles):
                        best_turtle = best_turtles[i % len(best_turtles)]  # Use modulo to cycle through the best turtles
                        worst_turtle.weight = best_turtle.weight
                        worst_turtle.direction_change_value = best_turtle.direction_change_value
                        worst_turtle.oscilation_factor = best_turtle.oscilation_factor
                        worst_turtle.size = best_turtle.size


                # Get all birds
                all_birds = list(filter(lambda i: type(i) == Bird, self.items))
                # Find the best birds (those that have eaten more than one turtle)
                best_birds = sorted(filter(lambda i: type(i) == Bird and i.eaten > 1, all_birds), key=lambda i: i.eaten, reverse=True)[:3]

                # If there are no best birds, generate random weights for all birds
                if not best_birds:
                    for bird in all_birds:
                        bird.weight = random.randrange(0, 100) / 100
                else:
                    # Find the worst birds (those that have not eaten any turtles)
                    worst_birds = sorted(filter(lambda bird: isinstance(bird, Bird) and bird.eaten == 0, all_birds), key=lambda bird: bird.eaten)[:3]

                    # If there are no worst birds, select 3 random birds to copy
                    if not worst_birds:
                        worst_birds = random.sample(all_birds, 3)

                    # Replace the attributes of the worst birds with those of the best birds
                    for i, worst_bird in enumerate(worst_birds):
                        best_bird = best_birds[i % len(best_birds)]  # Use modulo to cycle through the best birds
                        worst_bird.weight = best_bird.weight

                # Delete all tiles (rocks and sea)
                for tile in self.tiles:
                    self.canvas.delete(tile.inst)

                # make new map and rocks
                self.map = []
                self.map = create_map(40, 25)
                self.tiles = []
                for i in range(len(self.map)):
                    for j in range(len(self.map[i])):
                        if self.map[i][j] == 1:
                            self.tiles.append(Rock(self, j * 20, i * 20))
                        elif self.map[i][j] == 2:
                            self.tiles.append(Sea(self, j * 20, i * 20))
                for tile in self.tiles:
                    tile.draw(self.canvas)

                # delete all turtles
                for turtle in filter(lambda i: type(i) == Turtle, self.items):
                    self.canvas.delete(turtle.inst)
                    self.canvas.delete(turtle.dir_inst)
                    self.canvas.delete(turtle.turtle_number_inst)

                # delete all birds
                for bird in filter(lambda i: type(i) == Bird, self.items):
                    self.canvas.delete(bird.inst)
                    self.canvas.delete(bird.dir_inst)
                    self.canvas.delete(bird.bird_number_inst)

                # delete light and light lines
                for light in filter(lambda i: type(i) == Light, self.items):
                    self.canvas.delete(light.inst)
                    for line in light.lines:
                        self.canvas.delete(line)
                    light.lines.clear()

                # Define the number of segments
                num_segments = random.randint(6, 10)

                # Define the line segment range
                line_start_x = 100
                line_end_x = 750
                segment_width = (line_end_x - line_start_x) // num_segments

                # Remove all turtles from the items list
                self.items = list(filter(lambda i: type(i) != Turtle, self.items))

                # Respawn new turtles with mutated attributes
                for x in range(12):
                    # Randomly select a segment for the turtle to spawn in
                    segment_index = random.randint(0, num_segments - 1)
                    # Calculate the x-coordinate within the selected segment
                    segment_start = line_start_x + segment_index * segment_width
                    segment_end = segment_start + segment_width
                    turtle_x = random.randint(segment_start, segment_end)

                    # Add a small mutation to the attributes
                    new_random_minus10_to_10 = random.randrange(-100, 100) / 1000
                    new_weight = all_turtles[x].weight + new_random_minus10_to_10
                    new_dir = all_turtles[x].direction_change_value + new_random_minus10_to_10
                    new_osc = all_turtles[x].oscilation_factor + (new_random_minus10_to_10 * 100) / 3
                    new_siz = all_turtles[x].size + (new_random_minus10_to_10 * 2)

                    # print(f"Turtle {x+1} attributes after mutation:")
                    # print(f"Weight: {new_weight}, Direction: {new_dir}, Oscillation: {new_osc}, Size: {new_siz}\n")

                    # Create a new turtle with the mutated attributes and add it to the items list
                    self.items.append(Turtle(self, turtle_x, 100, new_weight, new_dir, new_osc, new_siz, x + 1))


                # Define the number of segments
                bird_num_segments = random.randint(2,5)

                # Define the line segment range
                bird_line_start_y = 100
                bird_line_end_y = 750
                bird_segment_width = (bird_line_end_y - bird_line_start_y) // bird_num_segments

                # Remove all birds from the items list
                self.items = list(filter(lambda i: type(i) != Bird, self.items))

                # Respawn new birds with mutated attributes
                for y in range(6):
                    # Randomly select a segment for the bird to spawn in
                    bird_segment_index = random.randint(0, bird_num_segments - 1)
                    # Calculate the y-coordinate within the selected segment
                    bird_segment_start = bird_line_start_y + bird_segment_index * bird_segment_width
                    bird_segment_end = bird_segment_start + bird_segment_width
                    bird_y = random.randint(bird_segment_start, bird_segment_end)

                    # Add a small mutation to the weight
                    new_bird_random_minus10_to_10 = random.randrange(-100, 100) / 1000
                    new_bird_weight = all_birds[y].weight + new_bird_random_minus10_to_10

                    # Print the mutated weight
                    print(f"Bird {y+1} weight after mutation: {new_bird_weight}\n")

                    # Create a new bird with the mutated weight and add it to the items list
                    self.items.append(Bird(self, bird_y, 300, new_bird_weight, y + 1))

                # respawn light
                self.items = list(filter(lambda i: type(i) != Light, self.items))
                for y in range(0,1):
                    self.items.append(Light(self, 400, 470))
                
           
            elif self.state == 3:
                print("Variant of Elitist Selection")
                size_list = []
                weight_list = []
                direction_list = []
                oscilation_list = []

                weight_list_bird = []
                
                self.iteration += 1
                self.all_dead_message_printed = False
                print("Iteration: ", self.iteration)
            

                # get surviving turtles, and get their weights (if there are no survivors, put randoms)
                surviving_turtles = list(filter(lambda i: type(i) == Turtle and i.water == True, self.items))
                if (len(surviving_turtles) == 0):
                    weight_list = [random.randrange(0, 100) / 100 for _ in range(0, 10)]
                    direction_list = [random.randrange(0, 300) / 100 for _ in range(0, 10)]
                    oscilation_list = [random.randrange(10, 30) for _ in range(0, 10)]
                    size_list = [random.randrange(0, 12) for _ in range(0, 10)]

                else:
                    if (len(surviving_turtles) > 3):
                        surviving_turtles = sorted(surviving_turtles, key=lambda i: i.life)

                        # if theres lots of survivsors, get the weights of the 3 best
                        weight_list.append(surviving_turtles[0].weight)
                        weight_list.append(surviving_turtles[1].weight)
                        weight_list.append(surviving_turtles[2].weight)

                        direction_list.append(surviving_turtles[0].direction_change_value)
                        direction_list.append(surviving_turtles[1].direction_change_value)
                        direction_list.append(surviving_turtles[2].direction_change_value)

                        oscilation_list.append(surviving_turtles[0].oscilation_factor)
                        oscilation_list.append(surviving_turtles[1].oscilation_factor)
                        oscilation_list.append(surviving_turtles[2].oscilation_factor)

                        size_list.append(surviving_turtles[0].size)
                        size_list.append(surviving_turtles[1].size)
                        size_list.append(surviving_turtles[2].size)
                    else:
                        for survivor in surviving_turtles:
                            weight_list.append(survivor.weight)
                            direction_list.append(survivor.direction_change_value)
                            oscilation_list.append(survivor.oscilation_factor)
                            size_list.append(survivor.size)

                # Get all birds that have eaten at least one turtle
                Birds_that_have_eaten = list(filter(lambda i: type(i) == Bird, self.items))

                if len(Birds_that_have_eaten) == 0:
                    weight_list_bird = [random.randrange(0, 100)/100 for _ in range(3)]
                else:
                    # Sort birds by 'eaten' attribute in descending order
                    Birds_that_have_eaten = sorted(Birds_that_have_eaten, key=lambda i: i.eaten)

                    if len(Birds_that_have_eaten) > 3:
                        weight_list_bird.append(Birds_that_have_eaten[0].weight)
                        weight_list_bird.append(Birds_that_have_eaten[1].weight)
                        weight_list_bird.append(Birds_that_have_eaten[2].weight)
                    else:
                        for survivor in Birds_that_have_eaten:
                            weight_list_bird.append(survivor.weight)
                    
                # Delete all tiles (rocks and sea)
                for tile in self.tiles:
                    self.canvas.delete(tile.inst)

                # make new map and rocks
                self.map = []
                self.map = create_map(40, 25)
                self.tiles = []
                for i in range(len(self.map)):
                    for j in range(len(self.map[i])):
                        if self.map[i][j] == 1:
                            self.tiles.append(Rock(self, j * 20, i * 20))
                        elif self.map[i][j] == 2:
                            self.tiles.append(Sea(self, j * 20, i * 20))
                for tile in self.tiles:
                    tile.draw(self.canvas)

                # delete all turtles
                for turtle in filter(lambda i: type(i) == Turtle, self.items):
                    self.canvas.delete(turtle.inst)
                    self.canvas.delete(turtle.dir_inst)
                    self.canvas.delete(turtle.turtle_number_inst)

                # delete all birds
                for bird in filter(lambda i: type(i) == Bird, self.items):
                    self.canvas.delete(bird.inst)
                    self.canvas.delete(bird.dir_inst)
                    self.canvas.delete(bird.bird_number_inst)

                # delete light and light lines
                for light in filter(lambda i: type(i) == Light, self.items):
                    self.canvas.delete(light.inst)
                    for line in light.lines:
                        self.canvas.delete(line)
                    light.lines.clear()

                # Define the number of segments
                num_segments = random.randint(6, 10)

                # Define the line segment range
                line_start_x = 100
                line_end_x = 750
                segment_width = (line_end_x - line_start_x) // num_segments

                # respawn new turtles with mutated weights
                self.items = list(filter(lambda i: type(i) != Turtle, self.items))
                for x in range(12):
                    # Randomly select a segment for the turtle to spawn in
                    segment_index = random.randint(0, num_segments - 1)
                    # Calculate the x-coordinate within the selected segment
                    segment_start = line_start_x + segment_index * segment_width
                    segment_end = segment_start + segment_width
                    turtle_x = random.randint(segment_start, segment_end)

                    random_minus10_to_10 = random.randrange(-100, 100) / 1000
                    weight = weight_list[random.randrange(0, len(weight_list))] + random_minus10_to_10
                    dir = direction_list[random.randrange(0, len(weight_list))] + random_minus10_to_10
                    osc = oscilation_list[random.randrange(0, len(oscilation_list))] + (random_minus10_to_10 * 100) / 3
                    siz = size_list[random.randrange(0, len(size_list))] + (random_minus10_to_10 * 2)
                    self.items.append(Turtle(self, turtle_x, 100, weight, dir, osc, siz, x + 1))

                # Define the number of segments
                bird_num_segments = random.randint(2,5)

                # Define the line segment range
                bird_line_start_y = 100
                bird_line_end_y = 750
                bird_segment_width = (bird_line_end_y - bird_line_start_y) // bird_num_segments

                # respawn new birds with mutated weights
                self.items = list(filter(lambda i: type(i) != Bird, self.items))
                for y in range(0, 6):
                    # Randomly select a segment for the turtle to spawn in
                    bird_segment_index = random.randint(0, bird_num_segments - 1)
                    # Calculate the x-coordinate within the selected segment
                    bird_segment_start = bird_line_start_y + bird_segment_index * bird_segment_width
                    bird_segment_end = bird_segment_start + bird_segment_width
                    bird_y = random.randint(bird_segment_start, bird_segment_end) 

                    random_minus10_to_10 = random.randrange(-100, 100) / 1000
                    weight = weight_list_bird[random.randrange(0, len(weight_list_bird))] + random_minus10_to_10
                    self.items.append(Bird(self, bird_y, 300, weight, y + 1))
                pass

                # respawn light
                self.items = list(filter(lambda i: type(i) != Light, self.items))
                for y in range(0,1):
                    self.items.append(Light(self, 400, 470))
                pass

            self.master.update()


def create_map(width, height):
    # 0 for sand
    map = [[0 for _ in range(width)] for _ in range(height)]
    # generate 2 for water
    for i in range(height - 8, height):
        map[i] = [2] * width
    # generate 1s for rock
    for i in range(height - 12, height - 8):
        map[i] = [1 if random.random() < 0.205 else 0 for _ in range(width)]
    return map


if __name__ == "__main__":
    m = create_map(40, 25)
    w = Window(m)
