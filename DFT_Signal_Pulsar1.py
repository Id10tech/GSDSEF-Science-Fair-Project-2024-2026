import numpy as np
import matplotlib.pyplot as plt

N = 20
m = np.arange(N)

#Respective amplitudes
A1 = 2 * 240.3411499
A2 = 2 * 323.6750783
A3 = 2 * 19.62380682
A4 = 2 * 49.5953873
A5 = 2 * 24.82707025
A6 = 2 * 3.716276805
A7 = 2 * 13.57305442
A8 = 2 * 24.24657408
A9 = 2 * 57.89750227
A10 = 33.87470998

#Phase in radians
phi1 = -1.168084937
phi2 = 1.279642856
phi3 = 2.892337571
phi4 = -1.593010231
phi5 = -1.561450804
phi6 = 0.301711856
phi7 = -2.921065905
phi8 = 1.31937808
phi9 = 0.245177689
phi10 = 1.05072E-13

#Generate cos components
x1 = A1 * np.cos(2*np.pi*1*m/N + phi1)
x2 = A2 * np.cos(2*np.pi*2*m/N + phi2)
x3 = A3 * np.cos(2*np.pi*3*m/N + phi3)
x4 = A4 * np.cos(2*np.pi*4*m/N + phi4)
x5 = A5 * np.cos(2*np.pi*5*m/N + phi5)
x6 = A6 * np.cos(2*np.pi*6*m/N + phi6)
x7 = A7 * np.cos(2*np.pi*7*m/N + phi7)
x8 = A8 * np.cos(2*np.pi*8*m/N + phi8)
x9 = A9 * np.cos(2*np.pi*9*m/N + phi9)
x10 = A10 * np.cos(2*np.pi*10*m/N + phi10)


#Sum
x_sum = x1 + x2 + x3 + x4 + x5 + x6 + x7 + x8 + x9 + x10

#Original signal
data = np.array([473.3178654, 44.08352668, 129.9303944, -431.5545244,
                 44.08352668, 250.5800464, 619.4895592, 839.9071926,
                 575.4060325, 512.7610209, 0, -436.1948956,
                 -918.7935035, -1111.36891, -1160.092807, -684.4547564,
                 -2.320185615, 382.8306265, 577.7262181, 294.6635731])

# Plot
plt.figure(figsize=(10,6))
plt.plot(m, x1, label='C1')
plt.plot(m, x2, label='C2')
plt.plot(m, x3, label='C3')
plt.plot(m, x4, label='C4')
plt.plot(m, x5, label='C5')
plt.plot(m, x6, label='C6')
plt.plot(m, x7, label='C7')
plt.plot(m, x8, label='C8')
plt.plot(m, x9, label='C9')
plt.plot(m, x10, label='C10')
plt.plot(m, x_sum, linewidth=2, label='Sum')
plt.plot(m, data, linestyle=':', linewidth=2, label='Original')

plt.xlabel('Sample n')
plt.ylabel('Amplitude')
plt.legend()
plt.grid(True)
plt.show()