import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time

data1 = np.random.rand(50)
data2 = np.random.rand(50)
data3 = np.random.rand(50)

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)

def animate(i):
    
    ax1.clear()
    ax1.plot(i)

n = 0
frames=[data1,data2,data3]
while True:
    ani = animation.FuncAnimation(fig, animate, frames=[data1,data2,data3])

    time.sleep(1)
    ani._draw_next_frame(frames[n%3],blit=True)
    
    n+=1