from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import json
import ast
import os

# Leer archivos Parquet
df_gamesf1 = pd.read_parquet(r'DataApi/games_f1.parquet')
df_itemsf1 = pd.read_parquet(r'DataApi/items_new.parquet')
df_itemsf2 = pd.read_parquet(r'DataApi/items_reducido.parquet')
df_games_f3 = pd.read_csv(r'DataApi/df_games.csv')
df_reviews_f3 = pd.read_csv(r'DataApi/df_reviews.csv')
df_games_ML = pd.read_csv(r'DataApi/games_ML.csv')

app = FastAPI()

def PlayTimeGenre(genero: str):
    # Filtro el DataFrame df_games por el género especificado
    df_filtrado = df_gamesf1[df_gamesf1['genres'].str.contains(genero, case=False, na=False)]

    if not df_filtrado.empty:
        # Uno df_filtrado con df_items en item_id para obtener las horas jugadas
        df_merged = pd.merge(df_filtrado, df_itemsf1, left_on='id', right_on='item_id', how='inner')

        # Encontrar el año con más horas jugadas para el género
        año_max_horas = df_merged.groupby('release_date')['playtime_forever'].sum().idxmax()

        return {"Año de lanzamiento con más horas jugadas para género " + genero: año_max_horas}
    else:
        return {"mensaje": "No se encontraron juegos para el género especificado"}
@app.get("/playtime_genre/{genero}")
async def get_playtime_genre(genero: str):
    try:
        return PlayTimeGenre(genero)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get('/UserForGenre')
def UserForGenre(genero: str):
    # Filtro el DataFrame df_games por el género especificado
    games_genre = df_gamesf1[df_gamesf1['genres'].str.contains(genero, case=False, na=False)]

    if not games_genre.empty:
        # Uno df_filtrado con df_items en item_id para obtener las horas jugadas y el usuario
        df_merged = pd.merge(games_genre, df_itemsf2, left_on='id', right_on='item_id', how='inner')
        # convierto en formato datetime la columna release_date
        df_merged['release_date'] = pd.to_datetime(df_merged['release_date'], errors='coerce')

        # Encontrar el usuario con más horas jugadas para el género
        usuario_max_horas = df_merged.groupby('user_id')['playtime_forever'].sum().idxmax()
        
        # Filtro  df_merged por el usuario con más horas jugadas
        df_usuario_max_horas = df_merged[df_merged['user_id'] == usuario_max_horas]

        # Agrupo por año y sumar las horas jugadas
        horas_por_año = df_usuario_max_horas.groupby(df_usuario_max_horas['release_date'].dt.year)['playtime_forever'].sum().reset_index()

        # Crear la estructura de retorno
        retorno = {
            "Usuario con más horas jugadas para género " + genero: usuario_max_horas,
            "Horas jugadas": [{"Año": año, "Horas": horas} for año, horas in zip(horas_por_año['release_date'], horas_por_año['playtime_forever'])]
        }

        return retorno
    else:
        return {"mensaje": "No se encontraron juegos para el género especificado"}    

@app.get('/UsersRecommend')
def UsersRecommend(año: int):
    # Uno los DataFrames de juegos y reseñas en 'id'
    df_merged = pd.merge(df_games_f3, df_reviews_f3, left_on='id', right_on='item_id', how='inner')

    # Filtro por reseñas positivas y por el año especificado
    df_filtered = df_merged[(df_merged['recommend'] == True) & (pd.to_datetime(df_merged['release_date'], errors= 'coerce').dt.year == año)]
    
    if not df_filtered.empty:
        # Agrupo por juego y contar las recomendaciones
        top_games = df_filtered.groupby('app_name')['recommend'].sum().reset_index()

        # Ordeno de forma descendente y tomar los primeros 3
        top_games = top_games.sort_values(by='recommend', ascending=False).head(3)

        # Crear la estructura de retorno
        retorno = [{"Puesto {}".format(i+1): juego} for i, juego in enumerate(top_games['app_name'])]

        return retorno
    else:
        return {"mensaje": "No hay juegos recomendados para el año especificado"}
    
@app.get('/UsersNotRecommend')
def UsersNotRecommend(año: int):
    # Uno los DataFrames de juegos y reseñas en 'id'
    df_merged = pd.merge(df_games_f3, df_reviews_f3, left_on='id', right_on='item_id', how='inner')

    # Filtro por reseñas negativas y por el año especificado
    df_filtered = df_merged[(df_merged['recommend'] == False) & (df_merged['sentiment_analysis'] == 0) & 
                            (pd.to_datetime(df_merged['release_date'], errors= 'coerce').dt.year == año)]

    if not df_filtered.empty:
        # Agrupo por juego y contar las no recomendaciones
        bottom_games = df_filtered.groupby('app_name')['recommend'].count().reset_index()

        # Ordeno de forma ascendente y tomar los primeros 3
        bottom_games = bottom_games.sort_values(by='recommend', ascending=True).head(3)

        # Crear la estructura de retorno
        retorno = [{"Puesto {}".format(i+1): juego} for i, juego in enumerate(bottom_games['app_name'])]

        return retorno
    else:
        return {"mensaje": "No hay juegos menos recomendados para el año especificado"}
    
@app.get('/sentiment_analysis')
def sentiment_analysis(año: int):
    # uno DataFrame games y reviews en 'id'
    df_merged = pd.merge(df_gamesf1, df_reviews_f3, left_on='id', right_on='item_id', how='inner')

    # Filtro por el año especificado
    df_filtered = df_merged[pd.to_datetime(df_merged['release_date'], errors='coerce').dt.year == año]

    if not df_filtered.empty:
        # Contar registros según el análisis de sentimiento
        sentiment_counts = df_filtered['sentiment_analysis'].value_counts().to_dict()

        # Mapear los valores para tener las etiquetas correspondientes
        sentiment_counts = {
            "Negative": sentiment_counts.get(0, 0),
            "Neutral": sentiment_counts.get(1, 0),
            "Positive": sentiment_counts.get(2, 0)
        }

        return sentiment_counts
    else:
        return {"mensaje": "No hay registros para el año especificado"}
    

def recomendacion_usuario(item_id):
    # Filtrar el DataFrame por el id especificado
    df_filtrado = df_games_ML[df_games_ML['id'] == item_id]

    # Obtener la lista de recomendaciones
    recomendaciones = df_filtrado['recomendaciones']

    return print(*recomendaciones, sep='\n')