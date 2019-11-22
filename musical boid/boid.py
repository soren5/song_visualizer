add_library('minim')
height3 = 0.0
height23 = 0.0
spectrumScale = 4.0
fftLin = None
fftLog = None
jingle = None
previous_colors = [
    (255, 255, 255),
    (255, 255, 255),
    (255, 255, 255),
    (255, 255, 255),
]
#pink_max = 102
#blue_max = 32
#yellow_max = 119
color_maxes =[
    50,
    15,
    20,
    30
]

width = 250
height = 250
circles = []
particles = []
particle_count = 6400 
memory = 0.5
circle_count = 3
break_chance = 1
colors_used = 4

def sigmoid(x):
    return 1 / (1 + exp(-x))
def distance_from_center(x, y):
    x = x - width / 2
    y = y - height / 2
    length = sqrt(x * x + y * y)
    return length

class Circle:
    def __init__(self, radius, x, y):
        self.radius = radius
        self.centerx = x
        self.centery = y

    def draw_circle(self):
        corner1_x = self.centerx - self.radius 
        corner1_y = self.centery - self.radius 
        corner2_x = self.centerx + self.radius 
        corner2_y = self.centery + self.radius 
        ellipse(corner1_x, corner1_y, corner2_x, corner2_y)

class Particle:
    def __init__(self, parent_circle, adversary_circle):
        self.parent_circle = parent_circle
        self.adversary_circle = adversary_circle
        self.circle = Circle(2, random(0,width), random(0,height))
        self.speed = [random(-1, 1), random(-1 , 1)]
        while not(self.check_circle(self.parent_circle) and not self.check_circle(self.adversary_circle)):
            self.circle.centerx = random(0, width)
            self.circle.centery = random(0, height)

    
    def check_circle(self, circle):
        length = distance_from_center(self.circle.centerx, self.circle.centery)
        if length < circle.radius:
            return True
        else:
            return False
    
    def update_position(self, percentage):
        percentage = pow(percentage, 1.5) * 5
        self.circle.centerx += self.speed[0] * percentage
        self.circle.centery += self.speed[1] * percentage
        if random(0, 1) < break_chance or (self.check_circle(self.parent_circle) and not self.check_circle(self.adversary_circle)):
            pass
        else:
            self.circle.centerx -= self.speed[0] * percentage
            self.circle.centery -= self.speed[1] * percentage
            self.speed[0] *= -1
            self.circle.centerx += self.speed[0] * percentage
            self.circle.centery += self.speed[1] * percentage
            if self.check_circle(self.parent_circle) and not self.check_circle(self.adversary_circle):
                pass
            else:
                self.circle.centerx -= self.speed[0] * percentage
                self.circle.centery -= self.speed[1] * percentage
                self.speed[0] *= -1
                self.speed[1] *= -1
                self.circle.centerx += self.speed[0] * percentage
                self.circle.centery += self.speed[1] * percentage
        if self.circle.centerx < 0 or self.circle.centerx > width or self.circle.centery < 0 or self.circle.centery > height:
            self.reinit()
    
    def reinit(self):
        #circle_index = int(random(0, 3))
        #self.parent_circle = circles[circle_index]
        #self.adversary_circle = circles[circle_index + 1]
        while not(self.check_circle(self.parent_circle) and not self.check_circle(self.adversary_circle)):
            self.circle.centerx = random(0, width)
            self.circle.centery = random(0, height) 
    



def setup():
    global fftLin, fftLog, jingle, height3, height23, maxes, width, height
    size(width, height, P2D)
    #fullScreen(P2D)
    height3 = height/3
    height23 = 2*height/3
    minim = Minim(this)
    colorMode(RGB, 255)
    ellipseMode(CORNERS)
    noStroke()
    jingle = minim.loadFile("Snail's House - Ma Chouchoute [Tasty Release].mp3", 1024)


    jingle.loop()
    #pink_max = get_freq_max(jingle, 0, 1, 10)
    #blue_max = get_freq_max(jingle, 1, 2, 10)
    #yellow_max = get_freq_max(jingle, 2, 10, 10)

    # create an FFT object that has a time-domain buffer the same size as jingle's sample buffer
    # note that this needs to be a power of two 
    # and that it means the size of the spectrum will be 1024. 
    # see the online tutorial for more info.
    circles.append(Circle(width * 2, width/2, height/2))
    circles.append(Circle(width / 2, width/2, height/2))
    circles.append(Circle(width / 4, width/2, height/2))
    circles.append(Circle(width / 6, width/2, height/2))
    circles.append(Circle(0,0,0))


    areas = []
    area_total = 0
    for i in circles:
        foo = i.radius * i.radius
        areas.append(foo)
        area_total += foo

    for i in range(particle_count):
        area_aux = 0
        for j in range(len(circles) - 1):
            area_aux += areas[j]
            if i / particle_count < area_aux / area_total:
                particles.append(Particle(circles[j], circles[j + 1]))
                break
        else:
            particles.append(Particle(circles[-2], circles[-1]))

    fftLin = FFT( jingle.bufferSize(), jingle.sampleRate() )

    # calculate the averages by grouping frequency bands linearly. use 30 averages.
    fftLin.linAverages( 30 )
  
    # create an FFT object for calculating logarithmically spaced averages
    fftLog = FFT( jingle.bufferSize(), jingle.sampleRate() )
    
    # calculate averages based on a miminum octave width of 22 Hz
    # split each octave into three bands
    # this should result in 30 averages
    fftLog.logAverages( 22, 3 )
    
    rectMode(CORNERS)
def get_mixed_color(color1, color2, percentage):
    return (
        color1[0] * percentage + color2[0] * (1 - percentage),
        color1[1] * percentage + color2[1] * (1 - percentage),
        color1[2] * percentage + color2[2] * (1 - percentage),
    )

def get_freq_total(start,end,slices):
    fftLinSize = int(fftLin.avgSize() / slices)
    freq_total = 0
    for i in range(fftLinSize * start, fftLinSize * end):
        freq_total += fftLin.getAvg(i)
    return freq_total

def draw():
    global previous_colors, color_maxes
    background(0)

    fftLin.forward( jingle.mix )
    fftLog.forward( jingle.mix )


    colors = [
        (255,113,206),
        (1,205,254),
        (5,255,161),
        (255,251,150),
        (185,103,255),
        #(255,255,255),
        (0,0,0),
    ]

    freq_totals = [
        get_freq_total(0,1,10),
        get_freq_total(1,2,10),
        get_freq_total(2,4,10),
        get_freq_total(4,10,10),
    ]

    #pink_max = pink_freq_total if pink_freq_total > pink_max else pink_max
    #blue_max = blue_freq_total if blue_freq_total > blue_max else blue_max
    #yellow_max = yellow_freq_total if yellow_freq_total > yellow_max else yellow_max
    #print('Pink Max: ', pink_max, '\nBlue Max: ', blue_max, '\nYellow Max: ', yellow_max)

    percentages = []
    for i in range(colors_used):
        percentages.append(freq_totals[i] / color_maxes[i])
    #pink_percentage = pink_freq_total / pink_max
    #blue_percentage = blue_freq_total / blue_max
    #yellow_percentage = yellow_freq_total / yellow_max


    tones = []
    for i in range(colors_used):
        tones.append(get_mixed_color(get_mixed_color(colors[i], colors[-1], percentages[i]), previous_colors[i], memory))
        previous_colors[i] = tones[i]

    """
    blue_tone = get_mixed_color(get_mixed_color(blue, gray, blue_percentage), previous_blue, memory)
    previous_blue = blue_tone
    #fill(aux_color[0], aux_color[1], aux_color[2])
    #circles[1].draw_circle()


    yellow_tone = get_mixed_color(get_mixed_color(yellow, gray, yellow_percentage), previous_yellow, memory)
    previous_yellow = yellow_tone
    #fill(aux_color[0], aux_color[1], aux_color[2])
    #circles[2].draw_circle()
    """

    for i in range(particle_count):
        for j in range(colors_used -1, -1 , -1):
            if particles[i].check_circle(circles[j]):
                fill(tones[j][0], tones[j][1], tones[j][2])
                particles[i].circle.draw_circle()
                particles[i].update_position(percentages[j])
                break