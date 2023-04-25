import numpy as np

deg = 2

coef = np.polyfit([2022, 2030, 2040], [100, 170, 300], deg)

b = [sum(coef[i] * x**(deg - i) for i in range(deg + 1)) for x in range(2022, 2045)]

# german excel format
print(" ".join(str(i).replace(".", ",") for i in b))
