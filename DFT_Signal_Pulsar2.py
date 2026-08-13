import numpy as np
import matplotlib.pyplot as plt

N = 20
m = np.arange(N)

#Respective amplitudes
A1 = 2 * 163.652716
A2 = 2 * 28.64621299
A3 = 2 * 24.76633431
A4 = 2 * 8.165692971
A5 = 2 * 1.894199246
A6 = 2 * 8.479879787
A7 = 2 * 23.38862762
A8 = 2 * 27.88979536
A9 = 2 * 17.61621273
A10 = 19.95157385

#Phase in radians
phi1 = 1.344505459
phi2 = 2.896996497
phi3 = 0.812268098
phi4 = 0.653173756
phi5 = 0.076771891
phi6 = 2.970839076
phi7 = -0.25150839
phi8 = -1.491557788
phi9 = -0.055693671
phi10 = 3.141592654

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
data = np.array([116.9007264, -95.20581114, -277.2881356, -168.8135593,
                 -317.9661017, -183.3414044, -195.9322034, -329.5883777,
                 -255.9806295, -179.4673123, -266.6343826, 81.0653753,
                 71.38014528, 292.2033898, 290.2663438, 402.6150121,
                 304.7941889, 264.1162228, 330.9443099, 115.9322034])

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