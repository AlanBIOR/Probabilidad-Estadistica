import pandas as pd
import numpy as np

db = pd.read_csv("db/iris.csv")
# db = pd.read_csv("db/iris.csv")
# db = pd.read_csv("db/generacion_liquidada_ago.csv", skiprows=7)
dict1 = db.to_dict(orient='records')

columnas = dict1[0].keys()

for columna in columnas:
    print(f"\n----------------------------------------")
    print(f"Columna analizada: {columna}")
    
    valores = [fila[columna] for fila in dict1]
    
    tipo_de_dato = type(valores[0])
    
    if tipo_de_dato == str:
        print("Esta columna no se puede calcular.")
        continue
        
    n = len(valores)
    x_prom = 0
    x_hm = 0
    x_geom = 1.0  
    es_valido = True
    es_valido_geom = True

    for x in valores:
        x_prom += x
        
        if x == 0:
            es_valido = False 
        else:
            x_hm += 1 / x
            
        if x <= 0:
            es_valido_geom = False
        else:
            if x_geom > 1e300:
                es_valido_geom = False
            else:
                x_geom *= float(x)

    # Resultados
    print(f"Promedio aritmético: {x_prom / n}")
    
    if es_valido and x_hm != 0:
        print(f"Media armónica: {n / x_hm}")
    else:
        print("Media armónica es n/0.")
        
    if es_valido_geom and x_geom > 0 and x_geom != float('inf'):
        print(f"Media geométrica: {x_geom ** (1/n)}")
    else:
        print("Media geométrica: El valor es demasiado grande o contiene ceros/negativos.")
