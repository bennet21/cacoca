import numpy as np

deg = 2

coef = np.polyfit([2022, 2030, 2040], [100, 170, 300], deg)

b = [sum(coef[i] * x**(deg - i) for i in range(deg + 1)) for x in range(2022, 2051)]

# csv format
print(','.join(f"{i:0.2f}" for i in b))

# german excel format
# print(" ".join(str(i).replace(".", ",") for i in b))
